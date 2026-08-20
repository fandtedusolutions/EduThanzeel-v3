from django.urls import path
from . import views

urlpatterns = [
    path('', views.tukuja, name='tukuja'),
    path('rsvp/', views.submit_rsvp, name='submit_rsvp'),
    path('dashboard/', views.tukuja_dashboard, name='tukuja_dashboard'),
    path('dashboard/export/', views.export_tukuja_excel, name='export_tukuja_excel'),
    path('dashboard/delete/<int:pk>/', views.delete_tukuja_rsvp, name='delete_tukuja_rsvp'),
]
