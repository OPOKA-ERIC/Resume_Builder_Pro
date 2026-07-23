from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Resume, Education, Experience, Skill, Project, Certification, Language, Reference
from .forms import (
    ResumeForm, EducationForm, ExperienceForm, SkillForm,
    ProjectForm, CertificationForm, LanguageForm, ReferenceForm
)


@login_required
def dashboard(request):
    resumes = Resume.objects.filter(user=request.user)
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

            if current_index < len(steps) - 1:
                return redirect('resumes:wizard_step', resume_id=resume.id, step=steps[current_index + 1])
            else:
                return redirect('resumes:template_select', resume_id=resume.id)
    else:
        form = form_class()

    existing_items = model.objects.filter(resume=resume) if model else []

    prev_step = steps[current_index - 1] if current_index > 0 else None

    return render(request, 'resumes/wizard_step.html', {
        'form': form,
        'resume': resume,
        'step': step,
        'step_index': current_index,
        'steps': steps,
        'existing_items': existing_items,
        'prev_step': prev_step,
    })


@login_required
def template_select(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    from templates_app.models import ResumeTemplate
    templates = ResumeTemplate.objects.filter(is_active=True)

    if request.method == 'POST':
        template_id = request.POST.get('template_id')
        if template_id:
            template = get_object_or_404(ResumeTemplate, id=template_id, is_active=True)
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
