from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Resume, Education, Experience, Skill, Project, Certification, Language, Reference
from .forms import (
    ResumeForm, EducationForm, ExperienceForm, SkillForm,
    ProjectForm, CertificationForm, LanguageForm, ReferenceForm
)


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
        form = ResumeForm(request.POST)
        if form.is_valid():
            resume = form.save(commit=False)
            resume.user = request.user
            resume.save()
            return redirect('resumes:wizard_step', resume_id=resume.id, step='education')
    else:
        form = ResumeForm()
    return render(request, 'resumes/resume_form.html', {'form': form, 'action': 'Create'})


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
    return render(request, 'resumes/preview.html', {'resume': resume})


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
