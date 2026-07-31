from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from django.views.decorators.clickjacking import xframe_options_sameorigin
from .models import Resume, Education, Experience, Skill, Project, Certification, Language, Reference
from .forms import (
    ResumeForm, EducationForm, ExperienceForm, SkillForm,
    ProjectForm, CertificationForm, LanguageForm, ReferenceForm
)


def _sample_data():
    """Return sample data dicts for pre-filling a resume from a template."""
    return {
        'educations': [
            {'institution': 'Stanford University', 'qualification': 'B.S. Computer Science',
             'start_year': 2018, 'end_year': 2022,
             'description': "GPA 3.8/4.0. Dean's List. Coursework: Data Structures, Algorithms, Machine Learning."},
        ],
        'experiences': [
            {'company': 'Google', 'role': 'Software Engineer',
             'start_year': 2022, 'end_year': None,
             'description': 'Developed and maintained core search infrastructure serving 5B+ daily queries. Led migration to microservices architecture, reducing latency by 40%. Mentored 3 junior engineers.'},
            {'company': 'Microsoft', 'role': 'Software Engineering Intern',
             'start_year': 2021, 'end_year': 2021,
             'description': 'Built internal dashboard tools using React and Python. Automated testing pipeline, increasing coverage from 60% to 85%.'},
        ],
        'skills': [
            {'name': 'Python', 'proficiency_level': 'expert'},
            {'name': 'JavaScript', 'proficiency_level': 'advanced'},
            {'name': 'React', 'proficiency_level': 'advanced'},
            {'name': 'Django', 'proficiency_level': 'advanced'},
            {'name': 'SQL', 'proficiency_level': 'intermediate'},
            {'name': 'AWS', 'proficiency_level': 'intermediate'},
        ],
        'projects': [
            {'name': 'Open Source Contribution', 'description': 'Active contributor to Django web framework with 50+ merged PRs.', 'link': 'https://github.com/django/django'},
            {'name': 'AI Resume Builder', 'description': 'Full-stack web application using Django, React, and GPT API.', 'link': 'https://github.com/alexj/resume-builder'},
        ],
        'certifications': [
            {'title': 'AWS Certified Solutions Architect', 'issuer': 'Amazon Web Services', 'year_awarded': 2023},
            {'title': 'Google Cloud Professional', 'issuer': 'Google', 'year_awarded': 2023},
        ],
        'languages': [
            {'name': 'English', 'proficiency_level': 'native'},
            {'name': 'Spanish', 'proficiency_level': 'fluent'},
            {'name': 'Mandarin', 'proficiency_level': 'basic'},
        ],
    'references': [
        {'name': 'Dr. Sarah Chen', 'relationship': 'Professor, Stanford University', 'contact': 'sarah.chen@stanford.edu'},
        {'name': 'Mark Williams', 'relationship': 'Engineering Manager, Google', 'contact': 'mark.w@google.com'},
    ],
}


SKILL_KEYWORDS = [
    'python', 'javascript', 'typescript', 'java', 'c++', 'go', 'rust', 'sql', 'nosql',
    'react', 'angular', 'vue', 'django', 'flask', 'node', 'express', 'html', 'css',
    'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'git', 'linux',
    'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch',
    'machine learning', 'data analysis', 'data science', 'nlp', 'tensorflow', 'pytorch',
    'excel', 'powerpoint', 'word', 'communication', 'leadership', 'project management',
    'agile', 'scrum', 'customer service', 'sales', 'marketing', 'seo', 'accounting',
    'finance', 'hr', 'recruiting', 'negotiation', 'problem solving', 'teamwork',
]


def _prefill_job_resume(resume):
    """Auto-fill a fresh job-linked resume from the job description + profile."""
    job = resume.job
    if not job:
        return False
    if resume.skills.exists() or resume.experiences.exists() or resume.educations.exists():
        return False
    user = resume.user
    profile = getattr(user, 'profile', None)
    full_name = user.get_full_name() or user.username
    user_city = (profile.city if profile else '') or ''
    location = user_city or job.location
    focus = job.requirements or (job.description[:300] if job.description else '')
    summary = (
        f'{full_name}, a professional based in {location}, is applying for the {job.title} role at '
        f'{job.employer.company_name} ({job.location}).\n\n'
        f'Key focus areas from the role: {focus}. {full_name} combines relevant experience with a '
        f'results-driven approach and strong collaboration skills.'
    )
    resume.summary = summary
    text = f"{job.description or ''} {job.requirements or ''}".lower()
    matched = []
    for keyword in SKILL_KEYWORDS:
        if keyword in text:
            name = keyword.title()
            if name not in matched:
                matched.append(name)
    if not matched:
        fallback = job.category.title() if job.category else 'Communication'
        matched = [fallback, 'Teamwork', 'Problem Solving']
    existing = {s.name.lower() for s in resume.skills.all()}
    for name in matched[:14]:
        if name.lower() not in existing:
            Skill.objects.create(resume=resume, name=name)
            existing.add(name.lower())
    if profile and profile.skills:
        for raw in profile.skills.split(','):
            name = raw.strip()
            if name and name.lower() not in existing:
                Skill.objects.create(resume=resume, name=name, proficiency_level='intermediate')
                existing.add(name.lower())
    if profile and profile.career_data:
        data = profile.career_data
        for item in data.get('education', []):
            Education.objects.create(resume=resume, **item)
        for item in data.get('experience', []):
            Experience.objects.create(resume=resume, **item)
        for item in data.get('projects', []):
            Project.objects.create(resume=resume, **item)
        for item in data.get('certifications', []):
            Certification.objects.create(resume=resume, **item)
        for item in data.get('languages', []):
            Language.objects.create(resume=resume, **item)
    resume.save()
    return True


RESUME_PAYMENT_PRICE = 9.99


def _safe_pay_next(request):
    next_url = request.POST.get('next') or request.GET.get('next') or ''
    if next_url.startswith('/') and not next_url.startswith('//'):
        return next_url
    return None


@login_required
def resume_pay(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    if resume.is_paid:
        messages.info(request, 'This resume is already paid — your CV is unlocked and you can apply to every approved job.')
        return redirect(_safe_pay_next(request) or 'jobs:job_list')
    if request.method == 'POST':
        resume.is_paid = True
        resume.paid_at = timezone.now()
        resume.save(update_fields=['is_paid', 'paid_at', 'updated_at'])
        messages.success(
            request,
            'Payment successful! Your CV is unlocked for download and you now have access to the application links for every approved job.',
        )
        next_url = _safe_pay_next(request)
        if next_url:
            return redirect(next_url)
        if resume.job:
            return redirect('jobs:job_detail', job_id=resume.job.id)
        return redirect('resumes:resume_preview', resume_id=resume.id)
    return render(request, 'resumes/pay.html', {
        'resume': resume,
        'price': RESUME_PAYMENT_PRICE,
        'next_url': _safe_pay_next(request),
    })


@login_required
def create_from_template(request, template_id):
    """Create a new resume pre-filled with sample data from a template."""
    from templates_app.models import ResumeTemplate
    template = get_object_or_404(ResumeTemplate, id=template_id, is_active=True)

    resume = Resume.objects.create(
        user=request.user,
        title='My Professional Resume',
        template=template,
    )

    data = _sample_data()

    for edu in data['educations']:
        Education.objects.create(resume=resume, **edu)
    for exp in data['experiences']:
        Experience.objects.create(resume=resume, **exp)
    for skill in data['skills']:
        Skill.objects.create(resume=resume, **skill)
    for proj in data['projects']:
        Project.objects.create(resume=resume, **proj)
    for cert in data['certifications']:
        Certification.objects.create(resume=resume, **cert)
    for lang in data['languages']:
        Language.objects.create(resume=resume, **lang)
    for ref in data['references']:
        Reference.objects.create(resume=resume, **ref)

    messages.success(request, f'Resume created with {template.name} template! You can now edit the sample data.')
    return redirect('resumes:resume_preview', resume_id=resume.id)


@login_required
def dashboard(request):
    resumes_list = Resume.objects.filter(user=request.user)
    paginator = Paginator(resumes_list, 9)
    page_number = request.GET.get('page')
    resumes = paginator.get_page(page_number)
    return render(request, 'resumes/dashboard.html', {'resumes': resumes})


@login_required
def resume_create(request):
    if request.method == 'POST':
        title = request.POST.get('title', 'My Professional Resume')
        resume = Resume.objects.create(user=request.user, title=title)
        return redirect('resumes:wizard_step', resume_id=resume.id, step='education')
    return render(request, 'resumes/resume_form.html', {'action': 'Create'})


@login_required
def wizard_step(request, resume_id, step):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)

    steps = ['education', 'experience', 'skills', 'projects', 'certifications', 'languages', 'references']
    current_index = steps.index(step) if step in steps else 0

    form_classes = {
        'education': EducationForm,
        'experience': ExperienceForm,
        'skills': SkillForm,
        'projects': ProjectForm,
        'certifications': CertificationForm,
        'languages': LanguageForm,
        'references': ReferenceForm,
    }

    model_map = {
        'education': Education,
        'experience': Experience,
        'skills': Skill,
        'projects': Project,
        'certifications': Certification,
        'languages': Language,
        'references': Reference,
    }

    form_class = form_classes.get(step)
    model = model_map.get(step)

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.resume = resume
            obj.save()
            messages.success(request, f'{step.title()} saved successfully.')

            if 'add_another' in request.POST:
                return redirect('resumes:wizard_step', resume_id=resume.id, step=step)

            if current_index < len(steps) - 1:
                return redirect('resumes:wizard_step', resume_id=resume.id, step=steps[current_index + 1])
            else:
                return redirect('resumes:template_select', resume_id=resume.id)
    else:
        form = form_class()

    existing_items = model.objects.filter(resume=resume) if model else []

    previous_step = steps[current_index - 1] if current_index > 0 else None

    return render(request, 'resumes/wizard_step.html', {
        'form': form,
        'resume': resume,
        'step': step,
        'step_index': current_index,
        'steps': steps,
        'existing_items': existing_items,
        'previous_step': previous_step,
    })


@login_required
def template_select(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    from templates_app.models import ResumeTemplate
    templates = ResumeTemplate.objects.filter(is_active=True)

    if request.method == 'POST':
        template_id = request.POST.get('template_id')
        if template_id:
            template = ResumeTemplate.objects.filter(id=template_id, is_active=True).first()
            if template:
                resume.template = template
                resume.save()
                if resume.job and not resume.is_paid and _prefill_job_resume(resume):
                    messages.success(
                        request,
                        f'Template "{template.name}" selected and auto-filled from the job description and your profile.',
                    )
                else:
                    messages.success(request, f'Template "{template.name}" selected.')
        return redirect('resumes:resume_preview', resume_id=resume.id)

    tag_filter = request.GET.get('tag', '')
    templates_list = list(templates)
    if tag_filter:
        templates_list = [t for t in templates_list if tag_filter in (t.tags or [])]
    all_tags = set()
    for t in templates:
        if t.tags:
            all_tags.update(t.tags)

    return render(request, 'resumes/template_select.html', {
        'resume': resume,
        'templates': templates_list,
        'all_tags': sorted(all_tags),
        'current_tag': tag_filter,
        'can_prefill': bool(resume.job and not resume.skills.exists()),
    })


@login_required
def _resolve_template_path(resume):
    """Return (template_path, context_updates) for a resume, handling skin vs legacy."""
    if not resume.template:
        return None, {}
    ctx = {}
    if resume.template.skin_file:
        template_path = resume.template.get_archetype_path()
    elif resume.template.html_file:
        template_path = resume.template.html_file
    else:
        return None, {}
    if resume.template.swatches:
        from pdf_export.views import _lighten_color
        ctx['accent'] = resume.template.swatches[0]
        ctx['accent_soft'] = _lighten_color(resume.template.swatches[0])
    return template_path, ctx


def resume_preview(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)

    pdf_html = None
    template_path, extra_ctx = _resolve_template_path(resume)
    if template_path:
        try:
            from django.template.loader import render_to_string
            context = {'resume': resume, 'user': request.user}
            context.update(extra_ctx)
            pdf_html = render_to_string(template_path, context)
        except Exception:
            pdf_html = None

    return render(request, 'resumes/preview.html', {
        'resume': resume,
        'pdf_html': pdf_html,
    })


def public_cv_view(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id)
    pdf_html = None
    if resume.template and resume.template.html_file:
        try:
            from django.template.loader import render_to_string
            pdf_html = render_to_string(resume.template.html_file, {
                'resume': resume,
                'user': resume.user,
            })
        except Exception:
            pdf_html = None
    return render(request, 'resumes/public_cv.html', {
        'resume': resume,
        'pdf_html': pdf_html,
    })


@login_required
@xframe_options_sameorigin
def resume_preview_frame(request, resume_id):
    """Return the rendered resume HTML as a standalone page (for iframe src)."""
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    template_path, extra_ctx = _resolve_template_path(resume)
    if template_path:
        try:
            from django.template.loader import render_to_string
            context = {'resume': resume, 'user': request.user}
            context.update(extra_ctx)
            html = render_to_string(template_path, context)
            return HttpResponse(html, content_type='text/html')
        except Exception:
            pass
    return HttpResponse('<p>No template selected.</p>', content_type='text/html')


@login_required
def resume_edit(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    if request.method == 'POST':
        form = ResumeForm(request.POST, instance=resume)
        if form.is_valid():
            form.save()
            messages.success(request, 'Resume updated.')
            return redirect('resumes:dashboard')
    else:
        form = ResumeForm(instance=resume)
    return render(request, 'resumes/resume_form.html', {'form': form, 'action': 'Edit', 'resume': resume})


@login_required
def resume_delete(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    if request.method == 'POST':
        resume.delete()
        messages.success(request, 'Resume deleted.')
        return redirect('resumes:dashboard')
    return render(request, 'resumes/resume_confirm_delete.html', {'resume': resume})


@login_required
def wizard_entry_edit(request, resume_id, step, entry_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)

    form_classes = {
        'education': EducationForm,
        'experience': ExperienceForm,
        'skills': SkillForm,
        'projects': ProjectForm,
        'certifications': CertificationForm,
        'languages': LanguageForm,
        'references': ReferenceForm,
    }
    model_map = {
        'education': Education,
        'experience': Experience,
        'skills': Skill,
        'projects': Project,
        'certifications': Certification,
        'languages': Language,
        'references': Reference,
    }

    model = model_map.get(step)
    form_class = form_classes.get(step)

    if not model or not form_class:
        return redirect('resumes:wizard_step', resume_id=resume.id, step=step)

    entry = get_object_or_404(model, id=entry_id, resume=resume)

    if request.method == 'POST':
        form = form_class(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            messages.success(request, f'{step.title()} updated successfully.')
            return redirect('resumes:wizard_step', resume_id=resume.id, step=step)
    else:
        form = form_class(instance=entry)

    return render(request, 'resumes/wizard_entry_form.html', {
        'form': form,
        'resume': resume,
        'step': step,
        'entry': entry,
    })


@login_required
def section_edit(request, resume_id, section, item_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    model_map = {
        'education': Education,
        'experience': Experience,
        'skills': Skill,
        'projects': Project,
        'certifications': Certification,
        'languages': Language,
        'references': Reference,
    }
    form_map = {
        'education': EducationForm,
        'experience': ExperienceForm,
        'skills': SkillForm,
        'projects': ProjectForm,
        'certifications': CertificationForm,
        'languages': LanguageForm,
        'references': ReferenceForm,
    }
    model = model_map.get(section)
    form_class = form_map.get(section)
    if not model or not form_class:
        messages.error(request, 'Invalid section.')
        return redirect('resumes:resume_preview', resume_id=resume.id)
    item = get_object_or_404(model, id=item_id, resume=resume)
    if request.method == 'POST':
        form = form_class(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, f'{section.title()} entry updated.')
            return redirect('resumes:resume_preview', resume_id=resume.id)
    else:
        form = form_class(instance=item)
    return render(request, 'resumes/section_edit.html', {
        'form': form, 'resume': resume, 'section': section, 'item': item,
    })


@login_required
def wizard_entry_delete(request, resume_id, step, entry_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)

    model_map = {
        'education': Education,
        'experience': Experience,
        'skills': Skill,
        'projects': Project,
        'certifications': Certification,
        'languages': Language,
        'references': Reference,
    }

    model = model_map.get(step)
    if not model:
        return redirect('resumes:wizard_step', resume_id=resume.id, step=step)

    entry = get_object_or_404(model, id=entry_id, resume=resume)

    if request.method == 'POST':
        entry.delete()
        messages.success(request, f'{step.title()} entry deleted.')
        return redirect('resumes:wizard_step', resume_id=resume.id, step=step)

    return render(request, 'resumes/wizard_entry_confirm_delete.html', {
        'resume': resume,
        'step': step,
        'entry': entry,
    })


@login_required
def section_delete(request, resume_id, section, item_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    model_map = {
        'education': Education,
        'experience': Experience,
        'skills': Skill,
        'projects': Project,
        'certifications': Certification,
        'languages': Language,
        'references': Reference,
    }
    model = model_map.get(section)
    if not model:
        messages.error(request, 'Invalid section.')
        return redirect('resumes:resume_preview', resume_id=resume.id)
    item = get_object_or_404(model, id=item_id, resume=resume)
    if request.method == 'POST':
        item.delete()
        messages.success(request, f'{section.title()} entry deleted.')
    return redirect('resumes:resume_preview', resume_id=resume.id)
