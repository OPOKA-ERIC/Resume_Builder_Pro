from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import ResumeTemplate


def template_gallery(request):
    templates = ResumeTemplate.objects.filter(is_active=True)
    return render(request, 'templates_app/gallery.html', {'templates': templates})


@login_required
def template_preview(request, template_id):
    template = get_object_or_404(ResumeTemplate, id=template_id)
    return render(request, 'templates_app/preview.html', {'template': template})
