from django.urls import path
from . import views

app_name = 'resumes'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('create/', views.resume_create, name='resume_create'),
    path('<int:resume_id>/edit/', views.resume_edit, name='resume_edit'),
    path('<int:resume_id>/delete/', views.resume_delete, name='resume_delete'),
    path('<int:resume_id>/wizard/<str:step>/', views.wizard_step, name='wizard_step'),
    path('<int:resume_id>/wizard/<str:step>/<int:entry_id>/edit/', views.wizard_entry_edit, name='wizard_entry_edit'),
    path('<int:resume_id>/wizard/<str:step>/<int:entry_id>/delete/', views.wizard_entry_delete, name='wizard_entry_delete'),
    path('<int:resume_id>/templates/', views.template_select, name='template_select'),
    path('<int:resume_id>/preview/', views.resume_preview, name='resume_preview'),
]
