from django.urls import path
from . import views

urlpatterns = [
    # Dashboard & main pages
    path('', views.dashboard, name='dashboard'),
    path('add-query/', views.add_query, name='add_query'),
    path('add-functionality/', views.add_functionality, name='add_functionality'),
    path('download-report-page/', views.download_report_page, name='download_report_page'),  # form page
    path('download-report/', views.download_report, name='download_report'),  # PDF/Word generation

    # Delete query
    path('delete-query/<int:query_id>/', views.delete_query, name='delete_query'),
    path('delete-functionality/<int:functionality_id>/', views.delete_functionality, name='delete_functionality'),
]
