from django.urls import path
from . import views

urlpatterns = [
    path('', views.tukuja, name='tukuja'),
    path('rsvp/', views.submit_rsvp, name='submit_rsvp'),
    path('pass/<str:registration_id>/', views.tukuja_pass, name='tukuja_pass'),
    path('coupon/<str:registration_id>/', views.tukuja_coupon, name='tukuja_coupon'),
    path('coupon/<str:registration_id>/image/', views.tukuja_coupon_image, name='tukuja_coupon_image'),
    path('scan/<str:registration_id>/', views.tukuja_scan, name='tukuja_scan'),
    path('dashboard/', views.tukuja_dashboard, name='tukuja_dashboard'),
    path('dashboard/leads/', views.tukuja_leads, name='tukuja_leads'),
    path('dashboard/converted/', views.tukuja_converted, name='tukuja_converted'),
    path('dashboard/food-batch/', views.tukuja_food_batch, name='tukuja_food_batch'),
    path('dashboard/export/', views.export_tukuja_excel, name='export_tukuja_excel'),
    path('dashboard/edit/<int:pk>/', views.edit_tukuja_lead, name='edit_tukuja_lead'),
    path('dashboard/convert/<int:pk>/', views.mark_tukuja_converted, name='mark_tukuja_converted'),
    path('dashboard/pending/<int:pk>/', views.mark_tukuja_pending, name='mark_tukuja_pending'),
    path('dashboard/whatsapp/<int:pk>/', views.send_tukuja_whatsapp, name='send_tukuja_whatsapp'),
    path('dashboard/delete/<int:pk>/', views.delete_tukuja_rsvp, name='delete_tukuja_rsvp'),
]
