from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.views.decorators.clickjacking import xframe_options_sameorigin
from .models import ResumeTemplate


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
                start_year=2018, end_year=2022,
                description='GPA 3.8/4.0. Dean\'s List. Coursework: Data Structures, Algorithms, Machine Learning.'),
        ]),
        experiences=_QuerySet([
            Obj(company='Google', role='Software Engineer',
                start_year=2022, end_year=None,
                description='Developed and maintained core search infrastructure serving 5B+ daily queries. Led migration to microservices architecture, reducing latency by 40%. Mentored 3 junior engineers.'),
            Obj(company='Microsoft', role='Software Engineering Intern',
                start_year=2021, end_year=2021,
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
            Obj(title='AWS Certified Solutions Architect', issuer='Amazon Web Services', year_awarded=2023),
            Obj(title='Google Cloud Professional', issuer='Google', year_awarded=2023),
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


def _render_template_with_theme(template, context, swatch=None, monochrome=False):
    """Render a template with theming support.
    
    For new templates (with skin_file), renders through the archetype system.
    For legacy templates (html_file only), renders directly.
    """
    theme_context = dict(context)
    
    # Apply swatch colors if provided
    if swatch and template.swatches:
        theme_context['accent'] = swatch
        # Generate a lighter version for accent-soft
        # Simple approach: use the swatch as accent, let CSS handle the rest
        theme_context['accent_soft'] = _lighten_color(swatch)
    
    if monochrome:
        theme_context['monochrome'] = True
    
    # Determine which template to render
    if template.skin_file:
        template_path = template.get_archetype_path()
    else:
        template_path = template.html_file
    
    try:
        return render_to_string(template_path, theme_context)
    except Exception as e:
        return f'<p>Failed to render template: {str(e)}</p>'


def _lighten_color(hex_color):
    """Convert a hex color to a light version for backgrounds."""
    hex_color = hex_color.lstrip('#')
    r, g, b = int(hex_color[:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    # Lighten by mixing with white (90% white)
    r = int(r + (255 - r) * 0.9)
    g = int(g + (255 - g) * 0.9)
    b = int(b + (255 - b) * 0.9)
    return f'#{r:02x}{g:02x}{b:02x}'


def template_gallery(request):
    templates = ResumeTemplate.objects.filter(is_active=True)
    
    # Get filter parameters
    tag_filter = request.GET.get('tag', '')
    templates_list = list(templates)
    
    if tag_filter:
        templates_list = [t for t in templates_list if tag_filter in (t.tags or [])]
    
    # Get all unique tags for the filter tabs
    all_tags = set()
    for t in templates:
        if t.tags:
            all_tags.update(t.tags)
    
    context = {
        'templates': templates_list,
        'all_tags': sorted(all_tags),
        'current_tag': tag_filter,
    }
    return render(request, 'templates_app/gallery.html', context)


@login_required
def template_preview(request, template_id):
    template = get_object_or_404(ResumeTemplate, id=template_id)
    ctx = _sample_context()
    ctx['template'] = template

    # Get swatch and monochrome from query params
    swatch = request.GET.get('swatch', None)
    monochrome = request.GET.get('monochrome', 'false').lower() == 'true'

    # Render the actual template HTML with sample data
    pdf_html = _render_template_with_theme(template, ctx, swatch=swatch, monochrome=monochrome)
    ctx['pdf_html'] = pdf_html
    ctx['current_swatch'] = swatch
    ctx['monochrome'] = monochrome

    return render(request, 'templates_app/preview.html', ctx)


@xframe_options_sameorigin
def template_preview_frame(request, template_id):
    """Return the rendered template HTML as a standalone page (for iframe src)."""
    template = get_object_or_404(ResumeTemplate, id=template_id)
    ctx = _sample_context()
    ctx['template'] = template
    
    # Get swatch and monochrome from query params
    swatch = request.GET.get('swatch', None)
    monochrome = request.GET.get('monochrome', 'false').lower() == 'true'
    
    html = _render_template_with_theme(template, ctx, swatch=swatch, monochrome=monochrome)

    # Inject normalization CSS to ensure consistent preview sizing
    normalize = (
        '<style id="preview-norm">'
        'html,body{margin:0!important;padding:0!important;overflow:hidden!important;width:100%!important}'
        '</style>'
    )
    head_close = html.find('</head>')
    if head_close != -1:
        html = html[:head_close] + normalize + html[head_close:]

    return HttpResponse(html, content_type='text/html')
