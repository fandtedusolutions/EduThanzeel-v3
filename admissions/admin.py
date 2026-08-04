from django.contrib import admin
from .models import AdmissionApplication, ContactInquiry, Achievement, Event, Course, Blog, Testimonial, HomePageVideo, TeamMember, Brochure, Notification

@admin.register(AdmissionApplication)
class AdmissionApplicationAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'course', 'mobile_number', 'created_at')
    list_filter = ('gender', 'age', 'course', 'created_at')
    search_fields = ('first_name', 'last_name', 'mobile_number', 'email', 'course')

@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'course_interest', 'phone_number', 'created_at')
    list_filter = ('course_interest', 'created_at')
    search_fields = ('full_name', 'email', 'phone_number', 'message', 'course_interest')

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title',)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'created_at')
    list_filter = ('date', 'created_at')
    search_fields = ('title',)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'created_at')
    list_filter = ('date', 'created_at')
    search_fields = ('title', 'content_p1', 'content_p2')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'created_at')
    search_fields = ('name', 'content')

@admin.register(HomePageVideo)
class HomePageVideoAdmin(admin.ModelAdmin):
    list_display = ('youtube_url', 'updated_at')

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'created_at')
    search_fields = ('name', 'role')

@admin.register(Brochure)
class BrochureAdmin(admin.ModelAdmin):
    list_display = ('updated_at',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('text', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('text',)
