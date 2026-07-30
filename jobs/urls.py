from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('', views.job_list, name='job_list'),
    path('<int:job_id>/', views.job_detail, name='job_detail'),
    path('<int:job_id>/apply/', views.apply_for_job, name='apply'),
    path('post/', views.post_job, name='post_job'),
    path('search/json/', views.job_search_json, name='job_search_json'),
    path('run-aggregation/', views.run_aggregation, name='run_aggregation'),
]
