from django.urls import path
from . import views

urlpatterns = [
    path('', views.my_favorites, name='my_favorites'),
    path('toggle/<int:listing_id>/', views.toggle_favorite, name='toggle_favorite'),
]