from django.urls import path
from . import views

app_name = 'portfolio'

urlpatterns = [
    path('', views.portfolio_list, name='list'),
    path('create/<int:resume_id>/', views.portfolio_create, name='create'),
    path('<int:portfolio_id>/', views.portfolio_manage, name='manage'),
    path('<int:portfolio_id>/toggle/', views.portfolio_toggle_publish, name='toggle'),
    path('<int:portfolio_id>/delete/', views.portfolio_delete, name='delete'),
]
