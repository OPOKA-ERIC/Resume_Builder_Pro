import hashlib
import logging
import threading
from django.conf import settings
from django.db.models import Avg
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import JobAnalysisForm
from .models import AnalysisTask, JobDescription, SkillGapAnalysis, JobPool
from .analyzer import analyze_match as _taxonomy_analyze
from .analyzer import analyze_match_from_text as _taxonomy_analyze_from_text
from .resume_parser import extract_text_from_upload
from .job_fetcher import fetch_job_from_url
from .job_searcher import search_jobs_for_resume
from .ai_parser import extract_job_details
from .gemini_matcher import analyze_match as _gemini_analyze_match
from resumes.models import Resume

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _resume_to_text(resume) -> str:
    parts = [f"Title: {resume.title}"]
    if hasattr(resume, 'summary') and resume.summary:
        parts.append(f"Summary: {resume.summary}")
    for exp in resume.experiences.all():
        parts.append(f"Experience: {exp.role} at {exp.company} ({exp.start_year}-{exp.end_year or 'Present'})")
        if exp.description:
            parts.append(exp.description)
    for edu in resume.educations.all():
        parts.append(f"Education: {edu.qualification} at {edu.institution} ({edu.start_year}-{edu.end_year or 'Present'})")
        if edu.description:
            parts.append(edu.description)
    for proj in resume.projects.all():
        parts.append(f"Project: {proj.name}")
        if proj.description:
            parts.append(proj.description)
    for cert in resume.certifications.all():
        parts.append(f"Certification: {cert.title} from {cert.issuer}")
    for lang in resume.languages.all():
        parts.append(f"Language: {lang.name} ({lang.proficiency_level})")
    skills = ', '.join(s.name for s in resume.skills.all())
    if skills:
        parts.append(f"Skills: {skills}")
    return '\n'.join(parts)


def _run_analysis(resume_text: str, job_text: str, resume=None) -> dict:
    if getattr(settings, 'GEMINI_API_KEY', None):
        try:
            result = _gemini_analyze_match(resume_text, job_text)
            if result and 'match_score' in result:
                return {
                    'overall_score': result['match_score'],
                    'matched_skills': result.get('matching_skills', []),
                    'missing_skills': result.get('missing_skills', []),
                    'partial_skills': [],
                    'recommendations': '\n'.join(result.get('suggested_improvements', [])),
                }
        except Exception as e:
            logger.warning('Gemini analysis failed, using taxonomy fallback: %s', e)

    if resume is not None:
        return _taxonomy_analyze(resume, job_text)
    return _taxonomy_analyze_from_text(resume_text, job_text)


def _set(task: AnalysisTask, step: str, progress: int):
    """Update task progress in-place and persist."""
    task.step = step
    task.progress = progress
    task.save(update_fields=['step', 'progress', 'updated_at'])


def _get_or_create_pool(user, resume, resume_text: str) -> JobPool:
    """Return the cached job pool for this resume, or create an empty one."""
    if resume is not None:
        pool = JobPool.objects.filter(user=user, resume=resume).order_by('-updated_at').first()
        fingerprint = ''
    else:
        fingerprint = hashlib.sha1(resume_text.encode('utf-8')).hexdigest()
        pool = JobPool.objects.filter(user=user, fingerprint=fingerprint).order_by('-updated_at').first()
    if pool is None:
        pool = JobPool.objects.create(user=user, resume=resume, fingerprint=fingerprint)
    return pool


# ---------------------------------------------------------------------------
# Background worker
# ---------------------------------------------------------------------------

def _run_task(task_id: str, user_id: int, payload: dict):
    """Runs in a daemon thread. Reads payload, does the work, updates task."""
    from django.contrib.auth.models import User

    try:
        task = AnalysisTask.objects.get(id=task_id)
        task.status = AnalysisTask.STATUS_RUNNING
        task.save(update_fields=['status', 'updated_at'])

        user = User.objects.get(id=user_id)
        source    = payload['source']
        jd_source = payload['jd_source']
        job_title = payload.get('job_title', '')
        company   = payload.get('company', '')
        job_text  = payload.get('job_description', '')

        # ── 1. Resume text ──────────────────────────────────────────────────
        _set(task, 'Extracting resume text…', 10)
        resume = None
        if source == 'existing':
            resume = Resume.objects.prefetch_related(
                'experiences', 'educations', 'projects',
                'certifications', 'languages', 'skills',
            ).get(id=payload['resume_id'], user=user)
            resume_text = _resume_to_text(resume)
        else:
            # Text was extracted in the view and stored in payload
            resume_text = payload['resume_text']

        # ── 2. Job description ──────────────────────────────────────────────
        if jd_source == 'autosearch':
            _set(task, 'Searching for matching jobs online…', 25)
            pool = _get_or_create_pool(user, resume, resume_text)
            job_descs = list(pool.jobs.all())

            if not job_descs:
                found = search_jobs_for_resume(resume_text)

                if not found:
                    task.status = AnalysisTask.STATUS_ERROR
                    task.error  = 'Could not find matching jobs. Try pasting a URL or description manually.'
                    task.save(update_fields=['status', 'error', 'updated_at'])
                    return

                job_descs = []
                for job in found:
                    job_descs.append(JobDescription.objects.create(
                        user=user,
                        title=job.get('title', ''),
                        company=job.get('company', ''),
                        location=job.get('location', ''),
                        raw_text=job.get('description', ''),
                        source_url='',
                    ))
                pool.jobs.set(job_descs)
                pool.save(update_fields=['updated_at'])
            else:
                _set(task, f'Re-using {len(job_descs)} previously found jobs — re-scoring…', 40)

            _set(task, f'Found {len(job_descs)} jobs — analysing…', 50)

            def _analyse_job(job_desc):
                result = _run_analysis(resume_text, job_desc.raw_text, resume=resume)
                return SkillGapAnalysis.objects.create(
                    job=job_desc,
                    resume=resume,
                    task=task,
                    overall_score=result['overall_score'],
                    matched_skills=result['matched_skills'],
                    missing_skills=result['missing_skills'],
                    partial_skills=result.get('partial_skills', []),
                    recommendations=result.get('recommendations', ''),
                )

            from concurrent.futures import ThreadPoolExecutor, as_completed
            analyses = []
            with ThreadPoolExecutor(max_workers=min(len(job_descs), 5)) as ex:
                futures = [ex.submit(_analyse_job, jd) for jd in job_descs]
                for f in as_completed(futures, timeout=15):
                    try:
                        analyses.append(f.result())
                    except Exception as e:
                        logger.warning('Job analysis failed: %s', e)

            if not analyses:
                task.status = AnalysisTask.STATUS_ERROR
                task.error  = 'All job analyses failed. Please try again.'
                task.save(update_fields=['status', 'error', 'updated_at'])
                return

            top = max(analyses, key=lambda a: a.overall_score)
            task.status      = AnalysisTask.STATUS_DONE
            task.progress    = 100
            task.step        = 'Complete'
            task.analysis_id = top.id
            task.save(update_fields=['status', 'progress', 'step', 'analysis_id', 'updated_at'])
            return

        if jd_source == 'url':
            _set(task, 'Fetching job posting from URL…', 25)
            fetched = fetch_job_from_url(payload['job_url'])

            if fetched['source'] == 'error':
                task.status = AnalysisTask.STATUS_ERROR
                task.error  = 'Could not fetch the URL. Try pasting the description manually.'
                task.save(update_fields=['status', 'error', 'updated_at'])
                return

            # Use fetched title/company directly — skip the extra Gemini parse call
            job_title = job_title or fetched.get('title', '')
            company   = company   or fetched.get('company', '')
            job_text  = fetched['description']

        # ── 3. Analyse ──────────────────────────────────────────────────────
        _set(task, 'Scoring your resume against the job…', 70)
        job_desc = JobDescription.objects.create(
            user=user,
            title=job_title or '',
            company=company or '',
            raw_text=job_text,
            source_url=payload.get('job_url', ''),
        )

        result = _run_analysis(resume_text, job_text, resume=resume)
        analysis = SkillGapAnalysis.objects.create(
            job=job_desc,
            resume=resume,
            task=task,
            overall_score=result['overall_score'],
            matched_skills=result['matched_skills'],
            missing_skills=result['missing_skills'],
            partial_skills=result.get('partial_skills', []),
            recommendations=result.get('recommendations', ''),
        )

        task.status      = AnalysisTask.STATUS_DONE
        task.progress    = 100
        task.step        = 'Complete'
        task.analysis_id = analysis.id
        task.save(update_fields=['status', 'progress', 'step', 'analysis_id', 'updated_at'])

    except Exception as exc:
        logger.exception('AnalysisTask %s failed', task_id)
        try:
            task = AnalysisTask.objects.get(id=task_id)
            task.status = AnalysisTask.STATUS_ERROR
            task.error  = str(exc)
            task.save(update_fields=['status', 'error', 'updated_at'])
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Views
# ---------------------------------------------------------------------------

@login_required
def analyze_view(request):
    form = JobAnalysisForm(request.POST or None, request.FILES or None, user=request.user)

    def context():
        analyses = SkillGapAnalysis.objects.filter(job__user=request.user)
        avg = analyses.aggregate(avg=Avg('overall_score'))['avg']
        return {
            'form': form,
            'has_resumes': request.user.resumes.exists(),
            'ai_available': bool(settings.GEMINI_API_KEY),
            'total_analyses': analyses.count(),
            'total_resumes': request.user.resumes.count(),
            'avg_score': round(avg) if avg is not None else None,
        }

    if request.method == 'POST' and form.is_valid():
        cd        = form.cleaned_data
        source    = cd['source']
        jd_source = cd['jd_source']

        payload = {
            'source':          source,
            'jd_source':       jd_source,
            'job_title':       cd.get('job_title', ''),
            'company':         cd.get('company', ''),
            'job_description': cd.get('job_description', ''),
            'job_url':         cd.get('job_url', ''),
        }

        if source == 'existing':
            payload['resume_id'] = int(cd['resume'])
        else:
            resume_file = request.FILES['resume_file']
            resume_text = extract_text_from_upload(resume_file)
            if not resume_text.strip():
                messages.error(request, 'Could not extract text from the uploaded file.')
                return render(request, 'job_match/analyze.html', context())
            payload['resume_text'] = resume_text

        task = AnalysisTask.objects.create(user=request.user, payload=payload)
        threading.Thread(
            target=_run_task, args=(str(task.id), request.user.id, payload), daemon=True
        ).start()

        return redirect('job_match:waiting', task_id=task.id)

    has_resumes = request.user.resumes.exists()
    return render(request, 'job_match/analyze.html', context())


@login_required
def waiting_view(request, task_id):
    task = get_object_or_404(AnalysisTask, id=task_id, user=request.user)
    # If already done/error when page loads, skip the waiting screen
    if task.status == AnalysisTask.STATUS_DONE and task.analysis_id:
        return redirect('job_match:results', analysis_id=task.analysis_id)
    return render(request, 'job_match/waiting.html', {'task_id': str(task_id)})


@login_required
def task_status(request, task_id):
    task = get_object_or_404(AnalysisTask, id=task_id, user=request.user)
    data = {
        'status':      task.status,
        'step':        task.step,
        'progress':    task.progress,
        'analysis_id': task.analysis_id,
        'error':       task.error,
    }
    return JsonResponse(data)


@login_required
def results_view(request, analysis_id):
    analysis = get_object_or_404(SkillGapAnalysis, id=analysis_id, job__user=request.user)
    total = (len(analysis.matched_skills) + len(analysis.missing_skills) +
             len(analysis.partial_skills))

    # For autosearch: surface all analyses created by the SAME task batch,
    # and always show the top-scoring match as the main card.
    all_analyses = None
    task = AnalysisTask.objects.filter(
        user=request.user, analysis_id=analysis_id
    ).first()
    if task:
        batch = list(task.analyses.select_related('job').order_by('-overall_score'))
        if batch and batch[0].id != analysis_id:
            return redirect('job_match:results', analysis_id=batch[0].id)
        all_analyses = batch or None

    return render(request, 'job_match/results.html', {
        'analysis': analysis,
        'total': total,
        'resume': analysis.resume,
        'all_analyses': all_analyses,
    })


@login_required
def history_view(request):
    analyses = SkillGapAnalysis.objects.filter(
        job__user=request.user
    ).select_related('job', 'resume')[:50]
    return render(request, 'job_match/history.html', {'analyses': analyses})


@login_required
def delete_analysis(request, analysis_id):
    analysis = get_object_or_404(SkillGapAnalysis, id=analysis_id, job__user=request.user)
    if request.method == 'POST':
        analysis.delete()
        messages.success(request, 'Analysis deleted successfully.')
    return redirect('job_match:history')
