from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
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
             'start_date': '2018-09-01', 'end_date': '2022-06-01',
             'description': "GPA 3.8/4.0. Dean's List. Coursework: Data Structures, Algorithms, Machine Learning."},
        ],
        'experiences': [
            {'company': 'Google', 'role': 'Software Engineer',
             'start_date': '2022-07-01', 'end_date': None,
             'description': 'Developed and maintained core search infrastructure serving 5B+ daily queries. Led migration to microservices architecture, reducing latency by 40%. Mentored 3 junior engineers.'},
            {'company': 'Microsoft', 'role': 'Software Engineering Intern',
             'start_date': '2021-06-01', 'end_date': '2021-09-01',
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
            {'title': 'AWS Certified Solutions Architect', 'issuer': 'Amazon Web Services', 'date_awarded': '2023-03-15'},
            {'title': 'Google Cloud Professional', 'issuer': 'Google', 'date_awarded': '2023-01-20'},
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
                messages.success(request, f'Template "{template.name}" selected.')
        return redirect('resumes:resume_preview', resume_id=resume.id)

    return render(request, 'resumes/template_select.html', {
        'resume': resume,
        'templates': templates,
    })


@login_required
def resume_preview(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)

    pdf_html = None
    if resume.template and resume.template.html_file:
        try:
            from django.template.loader import render_to_string
            from django.utils.html import escape as html_escape
            from django.utils.safestring import mark_safe
            raw_html = render_to_string(resume.template.html_file, {
                'resume': resume,
                'user': request.user,
            })
            pdf_html = mark_safe(html_escape(raw_html))
        except Exception:
            pdf_html = None

    return render(request, 'resumes/preview.html', {
        'resume': resume,
        'pdf_html': pdf_html,
    })


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

    steps = ['education', 'experience', 'skills', 'projects', 'certifications', 'languages', 'references']
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
