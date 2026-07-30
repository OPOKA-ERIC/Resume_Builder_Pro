from django.urls import path
from . import views

app_name = 'job_match'

urlpatterns = [
    path('', views.analyze_view, name='analyze'),
    path('results/<int:analysis_id>/', views.results_view, name='results'),
    path('history/', views.history_view, name='history'),
    path('delete/<int:analysis_id>/', views.delete_analysis, name='delete_analysis'),
]
