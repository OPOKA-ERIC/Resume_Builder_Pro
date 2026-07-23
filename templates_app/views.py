from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from .models import ResumeTemplate
import datetime


class _QuerySet:
    """Wraps a plain list to mimic Django queryset with .all() and iteration."""
    def __init__(self, items):
        self._items = list(items)
    def all(self):
        return self
    def __iter__(self):
        return iter(self._items)
    def __bool__(self):
        return bool(self._items)


def _sample_context():
    """Return sample resume data for template previews."""
    class Obj:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

    sample_user = Obj(
        get_full_name=lambda: 'Alex Johnson',
        username='alexjohnson',
        email='alex.johnson@email.com',
        profile=Obj(phone='+1 (555) 123-4567', address='San Francisco, CA'),
    )

    sample_resume = Obj(
        title='Software Engineer',
        educations=_QuerySet([
            Obj(institution='Stanford University', qualification='B.S. Computer Science',
                start_date=datetime.date(2018, 9, 1), end_date=datetime.date(2022, 6, 1),
                description='GPA 3.8/4.0. Dean\'s List. Coursework: Data Structures, Algorithms, Machine Learning.'),
        ]),
        experiences=_QuerySet([
            Obj(company='Google', role='Software Engineer',
                start_date=datetime.date(2022, 7, 1), end_date=None,
                description='Developed and maintained core search infrastructure serving 5B+ daily queries. Led migration to microservices architecture, reducing latency by 40%. Mentored 3 junior engineers.'),
            Obj(company='Microsoft', role='Software Engineering Intern',
                start_date=datetime.date(2021, 6, 1), end_date=datetime.date(2021, 9, 1),
                description='Built internal dashboard tools using React and Python. Automated testing pipeline, increasing coverage from 60% to 85%.'),
        ]),
        skills=_QuerySet([
            Obj(name='Python', proficiency_level='expert'),
            Obj(name='JavaScript', proficiency_level='advanced'),
            Obj(name='React', proficiency_level='advanced'),
            Obj(name='Django', proficiency_level='advanced'),
            Obj(name='SQL', proficiency_level='intermediate'),
            Obj(name='AWS', proficiency_level='intermediate'),
        ]),
        projects=_QuerySet([
            Obj(name='Open Source Contribution', description='Active contributor to Django web framework with 50+ merged PRs.', link='https://github.com/django/django'),
            Obj(name='AI Resume Builder', description='Full-stack web application using Django, React, and GPT API for intelligent resume generation.', link='https://github.com/alexj/resume-builder'),
        ]),
        certifications=_QuerySet([
            Obj(title='AWS Certified Solutions Architect', issuer='Amazon Web Services', date_awarded=datetime.date(2023, 3, 15)),
            Obj(title='Google Cloud Professional', issuer='Google', date_awarded=datetime.date(2023, 1, 20)),
        ]),
        languages=_QuerySet([
            Obj(name='English', proficiency_level='native'),
            Obj(name='Spanish', proficiency_level='fluent'),
            Obj(name='Mandarin', proficiency_level='basic'),
        ]),
        references=_QuerySet([
            Obj(name='Dr. Sarah Chen', relationship='Professor, Stanford University', contact='sarah.chen@stanford.edu'),
            Obj(name='Mark Williams', relationship='Engineering Manager, Google', contact='mark.w@google.com'),
        ]),
    )
    return {'resume': sample_resume, 'user': sample_user}


def template_gallery(request):
    templates = ResumeTemplate.objects.filter(is_active=True)
    return render(request, 'templates_app/gallery.html', {'templates': templates})


@login_required
def template_preview(request, template_id):
    template = get_object_or_404(ResumeTemplate, id=template_id)
    ctx = _sample_context()
    ctx['template'] = template

    # Render the actual template HTML with sample data
    try:
        pdf_html = render_to_string(template.html_file, ctx)
        ctx['pdf_html'] = pdf_html
    except Exception:
        ctx['pdf_html'] = None

    return render(request, 'templates_app/preview.html', ctx)


def template_preview_frame(request, template_id):
    """Return the rendered template HTML as a standalone page (for iframe src)."""
    template = get_object_or_404(ResumeTemplate, id=template_id)
    ctx = _sample_context()
    ctx['template'] = template
    try:
        html = render_to_string(template.html_file, ctx)
    except Exception:
        html = '<p>Failed to render template.</p>'
    return HttpResponse(html, content_type='text/html')
