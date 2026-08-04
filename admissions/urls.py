from django.urls import path
from . import views

urlpatterns = [
    # Main Site Template Views
    path('', views.index, name='home'),
    path('about/', views.about, name='about'),
    path('courses/', views.courses, name='courses'),
    path('contact-us/', views.contact, name='contact'),
    path('apply/', views.register, name='register'),
    path('blog/', views.blog, name='blog'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('gallery/', views.gallery, name='gallery'),
    
    # Course Details
    path('courses/basics/', views.course_detail_alm, name='alm'),
    path('courses/bayan/', views.course_detail_bayan, name='bayan'),
    path('courses/nuzul/', views.course_detail_nuzul, name='nuzul'),
    path('courses/hifz/', views.hifz, name='hifz'),
    path('courses/crash-course/', views.crash_course, name='crash'),

    # --- Admin Dashboard routes ---
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/admissions/', views.admin_admissions, name='admin_admissions'),
    path('dashboard/admissions/viewed/<int:pk>/', views.mark_admission_viewed, name='mark_admission_viewed'),
    path('dashboard/admissions/pending/<int:pk>/', views.unmark_admission_pending, name='unmark_admission_pending'),
    path('dashboard/admissions/soft-delete/<int:pk>/', views.soft_delete_admission, name='soft_delete_admission'),
    path('dashboard/admissions/recycle-bin/', views.recycle_bin_admissions, name='recycle_bin_admissions'),
    path('dashboard/admissions/restore/<int:pk>/', views.restore_admission, name='restore_admission'),
    path('dashboard/admissions/delete-permanent/<int:pk>/', views.delete_admission_permanent, name='delete_admission_permanent'),
    path('dashboard/admissions/export/', views.export_admissions_excel, name='export_admissions_excel'),
    
    path('dashboard/inquiries/', views.admin_inquiries, name='admin_inquiries'),
    path('dashboard/inquiries/viewed/<int:pk>/', views.mark_inquiry_viewed, name='mark_inquiry_viewed'),
    path('dashboard/inquiries/pending/<int:pk>/', views.unmark_inquiry_pending, name='unmark_inquiry_pending'),
    path('dashboard/inquiries/soft-delete/<int:pk>/', views.soft_delete_inquiry, name='soft_delete_inquiry'),
    path('dashboard/inquiries/recycle-bin/', views.recycle_bin_inquiries, name='recycle_bin_inquiries'),
    path('dashboard/inquiries/restore/<int:pk>/', views.restore_inquiry, name='restore_inquiry'),
    path('dashboard/inquiries/delete-permanent/<int:pk>/', views.delete_inquiry_permanent, name='delete_inquiry_permanent'),
    path('dashboard/inquiries/export/', views.export_inquiries_excel, name='export_inquiries_excel'),
    
    path('dashboard/achievements/', views.admin_achievements, name='admin_achievements'),
    path('dashboard/achievements/soft-delete/<int:pk>/', views.soft_delete_achievement, name='soft_delete_achievement'),
    path('dashboard/achievements/edit/<int:pk>/', views.edit_achievement, name='edit_achievement'),
    path('dashboard/achievements/recycle-bin/', views.recycle_bin_achievements, name='recycle_bin_achievements'),
    path('dashboard/achievements/restore/<int:pk>/', views.restore_achievement, name='restore_achievement'),
    path('dashboard/achievements/delete-permanent/<int:pk>/', views.delete_achievement_permanent, name='delete_achievement_permanent'),
    
    path('dashboard/events/', views.admin_events, name='admin_events'),
    path('dashboard/events/soft-delete/<int:pk>/', views.soft_delete_event, name='soft_delete_event'),
    path('dashboard/events/edit/<int:pk>/', views.edit_event, name='edit_event'),
    path('dashboard/events/recycle-bin/', views.recycle_bin_events, name='recycle_bin_events'),
    path('dashboard/events/restore/<int:pk>/', views.restore_event, name='restore_event'),
    path('dashboard/events/delete-permanent/<int:pk>/', views.delete_event_permanent, name='delete_event_permanent'),
    
    path('dashboard/courses/', views.admin_courses, name='admin_courses'),
    path('dashboard/courses/soft-delete/<int:pk>/', views.soft_delete_course, name='soft_delete_course'),
    path('dashboard/courses/edit/<int:pk>/', views.edit_course, name='edit_course'),
    path('dashboard/courses/recycle-bin/', views.recycle_bin_courses, name='recycle_bin_courses'),
    path('dashboard/courses/restore/<int:pk>/', views.restore_course, name='restore_course'),
    path('dashboard/courses/delete-permanent/<int:pk>/', views.delete_course_permanent, name='delete_course_permanent'),
    
    path('dashboard/blogs/', views.admin_blogs, name='admin_blogs'),
    path('dashboard/blogs/soft-delete/<int:pk>/', views.soft_delete_blog, name='soft_delete_blog'),
    path('dashboard/blogs/edit/<int:pk>/', views.edit_blog, name='edit_blog'),
    path('dashboard/blogs/recycle-bin/', views.recycle_bin_blogs, name='recycle_bin_blogs'),
    path('dashboard/blogs/restore/<int:pk>/', views.restore_blog, name='restore_blog'),
    path('dashboard/blogs/delete-permanent/<int:pk>/', views.delete_blog_permanent, name='delete_blog_permanent'),

    path('dashboard/testimonials/', views.admin_testimonials, name='admin_testimonials'),
    path('dashboard/testimonials/soft-delete/<int:pk>/', views.soft_delete_testimonial, name='soft_delete_testimonial'),
    path('dashboard/testimonials/edit/<int:pk>/', views.edit_testimonial, name='edit_testimonial'),
    path('dashboard/testimonials/recycle-bin/', views.recycle_bin_testimonials, name='recycle_bin_testimonials'),
    path('dashboard/testimonials/restore/<int:pk>/', views.restore_testimonial, name='restore_testimonial'),
    path('dashboard/testimonials/delete-permanent/<int:pk>/', views.delete_testimonial_permanent, name='delete_testimonial_permanent'),

    path('dashboard/video/', views.admin_video, name='admin_video'),
    path('dashboard/brochure/', views.admin_brochure, name='admin_brochure'),
    
    path('dashboard/team/', views.admin_team, name='admin_team'),
    path('dashboard/team/soft-delete/<int:pk>/', views.soft_delete_team, name='soft_delete_team'),
    path('dashboard/team/edit/<int:pk>/', views.edit_team, name='edit_team'),
    path('dashboard/team/recycle-bin/', views.recycle_bin_team, name='recycle_bin_team'),
    path('dashboard/team/restore/<int:pk>/', views.restore_team, name='restore_team'),
    path('dashboard/team/delete-permanent/<int:pk>/', views.delete_team_permanent, name='delete_team_permanent'),

    path('dashboard/notifications/', views.admin_notifications, name='admin_notifications'),
    path('dashboard/notifications/toggle/<int:pk>/', views.toggle_notification, name='toggle_notification'),
    path('dashboard/notifications/delete/<int:pk>/', views.delete_notification, name='delete_notification'),
    path('dashboard/notifications/edit/<int:pk>/', views.edit_notification, name='edit_notification'),

    # API Endpoints
    path('api/admission/', views.submit_admission, name='submit_admission'),
    path('api/contact/', views.submit_contact, name='submit_contact'),


    # Arabic Site Template 
    path('arabic_learn_for_kids/', views.arabic_learn_for_kids_index, name='arabic_learn_for_kids'),
    path('arabic_learn_ustad/', views.arabic_learn_ustad_index, name='arabic_learn_ustad'),
]

