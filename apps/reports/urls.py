from django.urls import path
from . import views

urlpatterns = [
    path('listing/<int:listing_id>/', views.report_listing, name='report_listing'),
]