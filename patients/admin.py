from django.contrib import admin
from django.utils.html import format_html
from .models import PatientProfile, MedicalRecord, PatientDocument, PatientNote


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    """Admin configuration for PatientProfile model"""
    
    list_display = [
        'user', 'user_name', 'user_phone', 'blood_group', 
        'is_active', 'created_at'
    ]
    list_filter = ['blood_group', 'is_active', 'created_at']
    search_fields = ['user__name', 'user__phone', 'user__email']
    ordering = ['-created_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Medical Information', {
            'fields': ('blood_group', 'allergies', 'chronic_conditions', 'current_medications')
        }),
        ('Insurance Information', {
            'fields': ('insurance_provider', 'insurance_policy_number', 'insurance_expiry')
        }),
        ('Preferences', {
            'fields': ('preferred_language', 'notification_preferences')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def user_name(self, obj):
        """Display user name"""
        return obj.user.name
    user_name.short_description = 'Name'
    
    def user_phone(self, obj):
        """Display user phone"""
        return obj.user.phone
    user_phone.short_description = 'Phone'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    """Admin configuration for MedicalRecord model"""
    
    list_display = [
        'patient', 'record_type', 'title', 'date_recorded', 
        'recorded_by', 'is_active', 'created_at'
    ]
    list_filter = ['record_type', 'date_recorded', 'is_active', 'created_at']
    search_fields = ['patient__name', 'title', 'description']
    ordering = ['-date_recorded']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('patient', 'record_type', 'title')
        }),
        ('Medical Details', {
            'fields': ('description', 'date_recorded', 'document')
        }),
        ('Author Information', {
            'fields': ('recorded_by',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('patient', 'recorded_by')


@admin.register(PatientDocument)
class PatientDocumentAdmin(admin.ModelAdmin):
    """Admin configuration for PatientDocument model"""
    
    list_display = [
        'patient', 'document_type', 'title', 'file_size_display', 
        'is_verified', 'verified_by', 'uploaded_at'
    ]
    list_filter = ['document_type', 'is_verified', 'uploaded_at']
    search_fields = ['patient__name', 'title', 'description']
    ordering = ['-uploaded_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('patient', 'document_type', 'title', 'description')
        }),
        ('File Information', {
            'fields': ('file',)
        }),
        ('Verification', {
            'fields': ('is_verified', 'verified_by', 'verified_at')
        }),
    )
    
    readonly_fields = ['verified_at', 'uploaded_at', 'updated_at']
    
    def file_size_display(self, obj):
        """Display file size in human readable format"""
        if obj.file and hasattr(obj.file, 'size'):
            size = obj.file.size
            if size < 1024:
                return f"{size} B"
            elif size < 1024 * 1024:
                return f"{size / 1024:.1f} KB"
            else:
                return f"{size / (1024 * 1024):.1f} MB"
        return "N/A"
    file_size_display.short_description = 'File Size'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('patient', 'verified_by')


@admin.register(PatientNote)
class PatientNoteAdmin(admin.ModelAdmin):
    """Admin configuration for PatientNote model"""
    
    list_display = [
        'patient', 'note_preview', 'is_private', 
        'created_by', 'created_at'
    ]
    list_filter = ['is_private', 'created_at']
    search_fields = ['patient__name', 'note']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('patient', 'note')
        }),
        ('Settings', {
            'fields': ('is_private',)
        }),
        ('Author Information', {
            'fields': ('created_by',)
        }),
    )
    
    readonly_fields = ['created_by', 'created_at', 'updated_at']
    
    def note_preview(self, obj):
        """Display note preview"""
        return obj.note[:50] + "..." if len(obj.note) > 50 else obj.note
    note_preview.short_description = 'Note Preview'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('patient', 'created_by')

