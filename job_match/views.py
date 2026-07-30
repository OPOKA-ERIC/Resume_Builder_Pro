import logging
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import JobAnalysisForm
from .models import JobDescription, SkillGapAnalysis
from .analyzer import analyze_match as _taxonomy_analyze
from .analyzer import analyze_match_from_text as _taxonomy_analyze_from_text
from .resume_parser import extract_text_from_upload
from .job_fetcher import fetch_job_from_url
from .job_searcher import search_jobs_for_resume
from .ai_parser import extract_job_details
from .gemini_matcher import analyze_match as _gemini_analyze_match
from resumes.models import Resume

logger = logging.getLogger(__name__)


def _resume_to_text(resume) -> str:
    parts = [f"Title: {resume.title}"]
    for exp in resume.experiences.all():
        parts.append(f"Experience: {exp.role} at {exp.company} ({exp.start_date}-{exp.end_date or 'Present'})")
        if exp.description:
            parts.append(exp.description)
    for edu in resume.educations.all():
        parts.append(f"Education: {edu.qualification} at {edu.institution} ({edu.start_date}-{edu.end_date or 'Present'})")
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


def _run_analysis(resume_text: str, job_text: str) -> dict:
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

    return _taxonomy_analyze_from_text(resume_text, job_text)


@login_required
def analyze_view(request):
    form = JobAnalysisForm(request.POST or None, request.FILES or None, user=request.user)

    if request.method == 'POST' and form.is_valid():
        source = form.cleaned_data['source']
        jd_source = form.cleaned_data['jd_source']
        job_title = form.cleaned_data.get('job_title', '')
        company = form.cleaned_data.get('company', '')
        job_text = form.cleaned_data.get('job_description', '')

        if source == 'existing':
            resume_id = int(form.cleaned_data['resume'])
            resume = get_object_or_404(Resume, id=resume_id, user=request.user)
            resume_text = _resume_to_text(resume) if resume.pk else ''
        else:
            resume_file = request.FILES['resume_file']
            resume_text = extract_text_from_upload(resume_file)
            if not resume_text.strip():
                messages.error(request, 'Could not extract text from the file.')
                return render(request, 'job_match/analyze.html', {
                    'form': form, 'has_resumes': request.user.resumes.exists(),
                    'ai_available': bool(settings.GEMINI_API_KEY),
                })

        if jd_source == 'autosearch':
            messages.info(request, 'AI is searching for matching jobs online...')
            jobs = search_jobs_for_resume(resume_text)

            if not jobs:
                messages.error(request, 'Could not find matching jobs online. Try pasting a URL or description manually.')
                return render(request, 'job_match/analyze.html', {
                    'form': form, 'has_resumes': request.user.resumes.exists(),
                    'ai_available': bool(settings.GEMINI_API_KEY),
                })

            messages.success(request, f'Found {len(jobs)} matching jobs. Analyzing...')

            analyses = []
            for job in jobs:
                job_desc = JobDescription.objects.create(
                    user=request.user,
                    title=job.get('title', ''),
                    company=job.get('company', ''),
                    raw_text=job.get('description', ''),
                    source_url='',
                )
                result = _run_analysis(resume_text, job.get('description', ''))
                analysis = SkillGapAnalysis.objects.create(
                    job=job_desc,
                    resume=resume if source == 'existing' else None,
                    overall_score=result['overall_score'],
                    matched_skills=result['matched_skills'],
                    missing_skills=result['missing_skills'],
                    partial_skills=result.get('partial_skills', []),
                    recommendations=result.get('recommendations', ''),
                )
                analyses.append(analysis)

            analyses.sort(key=lambda a: a.overall_score, reverse=True)
            top = analyses[0]

            if top.overall_score >= 80:
                messages.success(request, f'Best match: {top.job.title} ({top.overall_score:.0f}%)')
            elif top.overall_score >= 60:
                messages.info(request, f'Top match: {top.job.title} ({top.overall_score:.0f}%)')
            else:
                messages.warning(request, f'Best match found: {top.job.title} ({top.overall_score:.0f}%)')

            return render(request, 'job_match/results.html', {
                'analysis': top,
                'total': sum(len(a.matched_skills) + len(a.missing_skills) + len(a.partial_skills) for a in analyses),
                'resume': resume if source == 'existing' else None,
                'all_analyses': analyses,
            })

        if jd_source == 'url':
            job_url = form.cleaned_data['job_url']
            messages.info(request, 'Fetching job details with AI...')

            fetched = fetch_job_from_url(job_url)

            if fetched['source'] == 'error':
                messages.warning(request, 'Could not fetch the URL. You can paste the description manually instead.')
                return render(request, 'job_match/analyze.html', {
                    'form': form,
                    'has_resumes': request.user.resumes.exists(),
                    'ai_available': bool(settings.GEMINI_API_KEY),
                })

            parsed = extract_job_details(fetched['description'])

            if not job_title and parsed.get('title'):
                job_title = parsed['title']
            if not company and parsed.get('company'):
                company = parsed['company']
            if not job_text and parsed.get('description'):
                job_text = parsed['description']

            if not job_text:
                job_text = fetched['description']

            messages.success(request, f'AI extracted job details for "{job_title or "position"}".')

        job_desc = JobDescription.objects.create(
            user=request.user,
            title=job_title or '',
            company=company or '',
            raw_text=job_text,
            source_url=form.cleaned_data.get('job_url', ''),
        )

        result = _run_analysis(resume_text, job_text)
        analysis = SkillGapAnalysis.objects.create(
            job=job_desc,
            resume=resume if source == 'existing' else None,
            overall_score=result['overall_score'],
            matched_skills=result['matched_skills'],
            missing_skills=result['missing_skills'],
            partial_skills=result.get('partial_skills', []),
            recommendations=result.get('recommendations', ''),
        )
        logger.info(f"Analysis #{analysis.id}: {result['overall_score']}%")

        if result['overall_score'] >= 80:
            messages.success(request, 'Strong match! Your resume covers most required skills.')
        elif result['overall_score'] >= 60:
            messages.info(request, 'Good match. Check the recommendations to improve further.')
        elif result['overall_score'] >= 40:
            messages.warning(request, 'Moderate match. Consider addressing the skill gaps below.')
        else:
            messages.error(request, 'Low match. Your resume needs significant improvement for this role.')

        return redirect('job_match:results', analysis_id=analysis.id)

    has_resumes = request.user.resumes.exists()
    return render(request, 'job_match/analyze.html', {
        'form': form,
        'has_resumes': has_resumes,
        'ai_available': bool(settings.GEMINI_API_KEY),
    })


@login_required
def results_view(request, analysis_id):
    analysis = get_object_or_404(
        SkillGapAnalysis, id=analysis_id, job__user=request.user,
    )
    total = (len(analysis.matched_skills) + len(analysis.missing_skills) +
             len(analysis.partial_skills))
    return render(request, 'job_match/results.html', {
        'analysis': analysis, 'total': total, 'resume': analysis.resume,
    })


@login_required
def history_view(request):
    analyses = SkillGapAnalysis.objects.filter(
        job__user=request.user
    ).select_related('job', 'resume')[:50]
    return render(request, 'job_match/history.html', {'analyses': analyses})


@login_required
def delete_analysis(request, analysis_id):
    analysis = get_object_or_404(
        SkillGapAnalysis, id=analysis_id, job__user=request.user,
    )
    if request.method == 'POST':
        analysis.delete()
        messages.success(request, 'Analysis deleted successfully.')
    return redirect('job_match:history')
