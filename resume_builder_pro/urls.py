from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from portfolio import views as portfolio_views
from templates_app.models import ResumeTemplate


def landing_view(request):
    from resumes.models import Resume
    featured_templates = ResumeTemplate.objects.filter(is_active=True).order_by('?')[:6]
    return render(request, 'landing.html', {
        'featured_templates': featured_templates,
        'resume_count': Resume.objects.count(),
        'template_count': ResumeTemplate.objects.filter(is_active=True).count(),
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', landing_view, name='landing'),
    path('accounts/', include('accounts.urls')),
    path('resumes/', include('resumes.urls')),
    path('templates/', include('templates_app.urls')),
    path('pdf/', include('pdf_export.urls')),
    path('portfolio/', include('portfolio.urls')),
    path('p/<slug:slug>/', portfolio_views.public_portfolio_view, name='portfolio_public'),
    path('job-match/', include('job_match.urls')),
    path('jobs/', include('jobs.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
