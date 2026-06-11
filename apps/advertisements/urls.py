from django.urls import path
from . import views

urlpatterns = [
    path('reveal-phone/<int:listing_id>/', views.reveal_phone, name='reveal_phone'),
    path('click/<int:ad_id>/', views.ad_click, name='ad_click'),
]