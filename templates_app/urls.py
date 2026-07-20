from django.urls import path
from . import views

app_name = 'templates_app'

urlpatterns = [
    path('', views.template_gallery, name='gallery'),
    path('<int:template_id>/preview/', views.template_preview, name='preview'),
]
