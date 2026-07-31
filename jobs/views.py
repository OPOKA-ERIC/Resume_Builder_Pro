import requests
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from .models import Job, Employer, JobApplication
from .scam_detector import ScamDetector


def get_client_location(request):
    ip = request.META.get('REMOTE_ADDR', '')
    if ip == '127.0.0.1' or ip.startswith('192.168.'):
        return None
    try:
        resp = requests.get(f'https://ipapi.co/{ip}/json/', timeout=3)
        if resp.status_code == 200:
            data = resp.json()
            return {
                'city': data.get('city', ''),
                'region': data.get('region', ''),
                'country': data.get('country_name', ''),
                'latitude': data.get('latitude'),
                'longitude': data.get('longitude'),
            }
    except Exception:
        pass
    return None


def _resolve_user_location(request):
    if request.user.is_authenticated:
        profile = getattr(request.user, 'profile', None)
        if profile is not None and profile.city:
            return {
                'city': profile.city.split(',')[0].strip(),
                'region': '',
                'country': '',
                'latitude': profile.latitude,
                'longitude': profile.longitude,
            }
    gps_lat = request.GET.get('lat')
    gps_lng = request.GET.get('lng')
    if gps_lat and gps_lng:
        try:
            return {
                'city': '',
                'region': '',
                'country': '',
                'latitude': float(gps_lat),
                'longitude': float(gps_lng),
            }
        except ValueError:
            pass
    return get_client_location(request)


def job_list(request):
    query = request.GET.get('q', '')
    location = request.GET.get('location', '')
    category = request.GET.get('category', '')
    employment_type = request.GET.get('type', '')
    is_remote = request.GET.get('remote', '')
    sort = request.GET.get('sort', '-created_at')

    seven_days_ago = timezone.now() - timedelta(days=7)
    jobs = Job.objects.filter(status='approved', created_at__gte=seven_days_ago)

    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(employer__company_name__icontains=query)
        )

    if location:
        jobs = jobs.filter(
            Q(location__icontains=location) |
            Q(location__icontains=location.split(',')[0].strip())
        )

    if category:
        jobs = jobs.filter(category__iexact=category)

    if employment_type:
        jobs = jobs.filter(employment_type=employment_type)

    if is_remote:
        jobs = jobs.filter(is_remote=True)

    jobs = jobs.select_related('employer')

    user_location = _resolve_user_location(request)
    if user_location and not location and not query:
        jobs_sorted = []
        other_jobs = []
        lat, lng = user_location['latitude'], user_location['longitude']
        if lat and lng:
            for job in jobs:
                if job.latitude and job.longitude:
                    dist = ((float(job.latitude) - lat) ** 2 + (float(job.longitude) - lng) ** 2) ** 0.5
                    jobs_sorted.append((dist, job))
                else:
                    loc_lower = job.location.lower()
                    if user_location.get('city', '').lower() in loc_lower or user_location.get('region', '').lower() in loc_lower:
                        jobs_sorted.append((0, job))
                    else:
                        other_jobs.append(job)
            jobs_sorted.sort(key=lambda x: x[0])
            jobs = [job for _, job in jobs_sorted] + other_jobs
        else:
            city = user_location.get('city', '').lower()
            if city:
                nearby = [j for j in jobs if city in j.location.lower()]
                others = [j for j in jobs if city not in j.location.lower()]
                jobs = nearby + others

    valid_sorts = {
        '-created_at': '-created_at',
        'created_at': 'created_at',
        '-trust_score': '-trust_score',
        'trust_score': 'trust_score',
        '-salary_max': '-salary_max',
        'salary_max': 'salary_max',
    }
    if isinstance(jobs, list):
        pass
    else:
        jobs = jobs.order_by(valid_sorts.get(sort, '-created_at'))

    approved_7d = Job.objects.filter(status='approved', created_at__gte=seven_days_ago)
    categories = approved_7d.values_list('category', flat=True).distinct().exclude(category='').order_by('category')

    paginator = Paginator(jobs, 12) if not isinstance(jobs, list) else Paginator(jobs, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
        'location': location,
        'category': category,
        'employment_type': employment_type,
        'is_remote': is_remote,
        'sort': sort,
        'categories': categories,
        'user_location': user_location,
        'total_jobs': approved_7d.count(),
    }
    return render(request, 'jobs/job_list.html', context)


def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id, status='approved')
    user_has_resume = False
    user_has_paid_resume = False
    has_applied = False
    can_view_details = False
    job_resume = None
    payable_resume = None

    if request.user.is_authenticated:
        from resumes.models import Resume
        resumes_qs = Resume.objects.filter(user=request.user)
        job_resume = resumes_qs.filter(job=job).first()
        user_has_resume = resumes_qs.exists()
        user_has_paid_resume = resumes_qs.filter(is_paid=True).exists()
        has_applied = JobApplication.objects.filter(user=request.user, job=job).exists()
        can_view_details = has_applied or user_has_paid_resume
        if not user_has_paid_resume:
            payable_resume = job_resume or resumes_qs.order_by('-updated_at').first()

    show_paywall = job.requires_resume and not can_view_details

    seven_days_ago = timezone.now() - timedelta(days=7)
    related_jobs = Job.objects.filter(
        status='approved',
        created_at__gte=seven_days_ago,
        category=job.category
    ).exclude(id=job.id)[:3]

    context = {
        'job': job,
        'related_jobs': related_jobs,
        'user_has_resume': user_has_resume,
        'user_has_paid_resume': user_has_paid_resume,
        'has_applied': has_applied,
        'job_resume': job_resume,
        'payable_resume': payable_resume,
        'can_view_details': can_view_details,
        'show_paywall': show_paywall,
    }
    return render(request, 'jobs/job_detail.html', context)


@login_required
def create_job_resume(request, job_id):
    job = get_object_or_404(Job, id=job_id, status='approved')

    from resumes.models import Resume
    existing = Resume.objects.filter(user=request.user, job=job).first()
    if existing:
        messages.info(request, f'You already have a resume tailored for {job.title}. Finish it and apply below.')
        return redirect('jobs:job_detail', job_id=job.id)

    resume = Resume.objects.create(
        user=request.user,
        job=job,
        title=f'{job.title} — {job.employer.company_name}',
        summary=f'Professional applying for the {job.title} role at {job.employer.company_name}'
                f' ({job.location}).',
    )
    messages.success(
        request,
        f'Resume created for {job.title} at {job.employer.company_name}. '
        f'Choose a template to auto-fill it from the job and your profile, or build it yourself with the wizard.',
    )
    return redirect('resumes:template_select', resume_id=resume.id)


@login_required
def apply_for_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, status='approved')

    if JobApplication.objects.filter(user=request.user, job=job).exists():
        messages.info(request, 'You have already applied for this position.')
        return redirect('jobs:job_detail', job_id=job.id)

    from resumes.models import Resume
    user_resume = Resume.objects.filter(user=request.user, job=job).first()
    if not user_resume:
        messages.warning(
            request,
            f'You must create a resume tailored for {job.title} at {job.employer.company_name} '
            f'before you can apply. Use the description and requirements to build it.',
        )
        return redirect('jobs:create_job_resume', job_id=job.id)

    if not user_resume.is_paid:
        messages.warning(
            request,
            f'Your resume for {job.title} is ready but not yet paid. '
            f'Complete the one-time payment to unlock the application link for this and every other job.',
        )
        return redirect('resumes:resume_pay', resume_id=user_resume.id)

    JobApplication.objects.create(user=request.user, job=job, resume=user_resume)
    messages.success(request, f'You have successfully applied for {job.title} at {job.employer.company_name}!')
    if job.application_url:
        return redirect(job.application_url)
    return redirect('jobs:job_detail', job_id=job.id)


@login_required
def post_job(request):
    if request.method == 'POST':
        company_name = request.POST.get('company_name', '').strip()
        email = request.POST.get('email', '').strip()
        website = request.POST.get('website', '').strip()
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        requirements = request.POST.get('requirements', '').strip()
        responsibilities = request.POST.get('responsibilities', '').strip()
        location = request.POST.get('location', '').strip()
        is_remote = request.POST.get('is_remote') == 'on'
        salary_min = request.POST.get('salary_min', '').strip()
        salary_max = request.POST.get('salary_max', '').strip()
        employment_type = request.POST.get('employment_type', 'full_time')
        category = request.POST.get('category', '').strip()
        application_email = request.POST.get('application_email', '').strip()
        application_instructions = request.POST.get('application_instructions', '').strip()

        if not all([company_name, email, title, description, location]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'jobs/post_job.html')

        employer, created = Employer.objects.get_or_create(
            company_name=company_name,
            defaults={
                'email': email,
                'website': website,
                'registered_by': request.user,
            }
        )

        job_data = {
            'title': title,
            'description': description,
            'requirements': requirements,
            'responsibilities': responsibilities,
            'location': location,
            'is_remote': is_remote,
            'salary_min': float(salary_min) if salary_min else None,
            'salary_max': float(salary_max) if salary_max else None,
            'employment_type': employment_type,
            'category': category,
            'application_email': application_email or email,
            'application_instructions': application_instructions,
            'source': 'employer',
        }

        employer_data = {
            'company_name': company_name,
            'email': email,
            'website': website,
            'description': '',
        }

        detector = ScamDetector(job_data, employer_data)
        result = detector.run_all_checks()
        trust_score = result['score']

        is_auto_approved = trust_score >= 80 and created is False

        job = Job.objects.create(
            employer=employer,
            trust_score=trust_score,
            verification_details=result,
            status='approved' if is_auto_approved else 'pending',
            **job_data
        )

        if is_auto_approved:
            messages.success(request, 'Your job has been verified and posted successfully!')
            return redirect('jobs:job_detail', job_id=job.id)
        messages.info(request, 'Your job has been submitted for review. We will notify you once it is approved.')
        return redirect('jobs:job_list')

    return render(request, 'jobs/post_job.html')


def job_search_json(request):
    query = request.GET.get('q', '')
    location = request.GET.get('location', '')
    seven_days_ago = timezone.now() - timedelta(days=7)
    jobs = Job.objects.filter(status='approved', created_at__gte=seven_days_ago)

    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) |
            Q(employer__company_name__icontains=query) |
            Q(category__icontains=query)
        )
    if location:
        jobs = jobs.filter(location__icontains=location)

    jobs = jobs.select_related('employer').order_by('-created_at')[:10]
    results = [{
        'id': j.id,
        'title': j.title,
        'company': j.employer.company_name,
        'location': j.location,
        'salary_range': j.salary_range,
        'employment_type': j.get_employment_type_display(),
        'category': j.category,
        'trust_score': j.trust_score,
    } for j in jobs]

    return JsonResponse({'results': results})


def run_aggregation(request):
    if not request.user.is_staff:
        messages.error(request, 'Admin access required.')
        return redirect('jobs:job_list')

    from .aggregator import JobAggregator
    aggregator = JobAggregator()
    results = aggregator.aggregate_all()
    messages.success(request, f'Aggregation complete: {results.get("total", 0)} new jobs added.')
    return redirect('jobs:job_list')
