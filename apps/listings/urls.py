from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('rooms/landlord-dashboard/', views.landlord_dashboard, name='landlord_dashboard'),

    path('rooms/create/', views.create_listing, name='create_listing'),
    path('rooms/my-listings/', views.my_listings, name='my_listings'),

    path('rooms/<int:pk>/edit/', views.edit_listing, name='edit_listing'),
    path('rooms/<int:pk>/delete/', views.delete_listing, name='delete_listing'),

    path('rooms/images/<int:pk>/delete/', views.delete_listing_image, name='delete_listing_image'),
    path('rooms/images/<int:pk>/primary/', views.set_primary_image, name='set_primary_image'),

    path('rooms/<int:pk>/', views.listing_detail, name='listing_detail'),

    path('ajax/load-districts/', views.load_districts, name='load_districts'),
]