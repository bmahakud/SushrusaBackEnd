from django.contrib import admin
from .models import Clinic

@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'name', 'admin', 'consultation_duration', 'is_active', 'is_verified', 'created_at'
    ]
    list_filter = ['is_active', 'is_verified', 'city', 'state', 'country']
    search_fields = ['name', 'admin__name', 'city', 'state', 'country', 'registration_number']
    ordering = ['-created_at']
    readonly_fields = ['id', 'created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'name', 'clinic_type', 'description', 'admin')
        }),
        ('Contact Information', {
            'fields': ('phone', 'email', 'website')
        }),
        ('Address', {
            'fields': ('street', 'city', 'state', 'pincode', 'country', 'latitude', 'longitude')
        }),
        ('Operating Hours', {
            'fields': ('operating_hours',)
        }),
        ('Specialties & Services', {
            'fields': ('specialties', 'services', 'facilities')
        }),
        ('Registration & Licensing', {
            'fields': ('registration_number', 'license_number', 'accreditation')
        }),
        ('Media', {
            'fields': ('cover_image', 'gallery_images')
        }),
        ('Status', {
            'fields': ('is_active', 'is_verified', 'accepts_online_consultations')
        }),
        ('Consultation Settings', {
            'fields': ('consultation_duration',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
