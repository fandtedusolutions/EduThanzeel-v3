from django.contrib import admin
from .models import Rsvp


@admin.register(Rsvp)
class RsvpAdmin(admin.ModelAdmin):
    list_display = (
        'registration_id',
        'name',
        'phone_number',
        'attending_members',
        'attending_children',
        'created_at',
    )
    search_fields = ('registration_id', 'name', 'phone_number')
    list_filter = ('created_at',)
