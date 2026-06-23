from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),

    path('listings/pending/', views.pending_listings, name='pending_listings'),
    path('listings/approved/', views.approved_listings, name='approved_listings'),
    path('listings/rejected/', views.rejected_listings, name='rejected_listings'),

    path('listings/<int:pk>/review/', views.review_listing, name='review_listing'),
    path('listings/<int:pk>/approve/', views.approve_listing, name='approve_listing'),
    path('listings/<int:pk>/reject/', views.reject_listing, name='reject_listing'),

    path('reports/', views.reports_queue, name='reports_queue'),
    path('reports/<int:pk>/review/', views.review_report, name='review_report'),
    path('reports/<int:pk>/update/', views.update_report_status, name='update_report_status'),
    path('reports/<int:pk>/remove-listing/', views.remove_reported_listing, name='remove_reported_listing'),
    
    path('ads/', views.ads_dashboard, name='ads_dashboard'),
    path('ads/<int:pk>/toggle/', views.toggle_ad_status, name='toggle_ad_status'),
    path('ads/<int:pk>/delete/', views.delete_ad, name='delete_ad'),
]