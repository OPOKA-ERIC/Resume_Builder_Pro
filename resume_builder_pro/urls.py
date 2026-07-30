from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from portfolio import views as portfolio_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='landing.html'), name='landing'),
    path('accounts/', include('accounts.urls')),
    path('resumes/', include('resumes.urls')),
    path('templates/', include('templates_app.urls')),
    path('pdf/', include('pdf_export.urls')),
    path('portfolio/', include('portfolio.urls')),
    path('p/<slug:slug>/', portfolio_views.public_portfolio_view, name='portfolio_public'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
