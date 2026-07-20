from django.urls import path
from . import views

app_name = 'pdf_export'

urlpatterns = [
    path('<int:resume_id>/download/', views.download_pdf, name='download_pdf'),
    path('<int:resume_id>/preview/', views.pdf_preview, name='pdf_preview'),
]
