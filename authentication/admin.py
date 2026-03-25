from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, OTP, UserSession


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for User model"""
    
    list_display = [
        'id', 'name', 'phone', 'email', 'role', 'is_active', 
        'is_verified', 'date_joined', 'last_login'
    ]
    list_filter = ['role', 'is_active', 'is_verified', 'gender', 'date_joined']
    search_fields = ['name', 'phone', 'email', 'id']
    ordering = ['-date_joined']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'phone', 'email', 'name', 'role')
        }),
        ('Personal Information', {
            'fields': (
                'date_of_birth', 'gender', 'profile_picture',
                'blood_group', 'allergies', 'medical_history'
            )
        }),
        ('Address Information', {
            'fields': ('street', 'city', 'state', 'pincode', 'country')
        }),
        ('Emergency Contact', {
            'fields': (
                'emergency_contact_name', 'emergency_contact_phone', 
                'emergency_contact_relationship'
            )
        }),
        ('Status & Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser', 'is_verified',
                'groups', 'user_permissions'
            )
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )
    
    readonly_fields = ['id', 'date_joined', 'last_login']
    
    add_fieldsets = (
        ('Basic Information', {
            'classes': ('wide',),
            'fields': ('phone', 'name', 'role', 'password1', 'password2'),
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    """Admin configuration for OTP model"""
    
    list_display = [
        'phone', 'otp', 'purpose', 'is_used', 'is_expired_status',
        'created_at', 'expires_at'
    ]
    list_filter = ['purpose', 'is_used', 'created_at']
    search_fields = ['phone', 'otp']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'is_expired_status']
    
    def is_expired_status(self, obj):
        """Display expiry status with color coding"""
        if obj.is_expired:
            return format_html(
                '<span style="color: red;">Expired</span>'
            )
        else:
            return format_html(
                '<span style="color: green;">Valid</span>'
            )
    is_expired_status.short_description = 'Status'
    
    def has_add_permission(self, request):
        """Disable manual OTP creation"""
        return False


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    """Admin configuration for UserSession model"""
    
    list_display = [
        'user', 'device_info_short', 'ip_address', 'is_active',
        'created_at', 'last_used'
    ]
    list_filter = ['is_active', 'created_at', 'last_used']
    search_fields = ['user__name', 'user__phone', 'device_info', 'ip_address']
    ordering = ['-last_used']
    readonly_fields = ['created_at', 'last_used', 'refresh_token']
    
    def device_info_short(self, obj):
        """Display shortened device info"""
        if len(obj.device_info) > 50:
            return obj.device_info[:50] + '...'
        return obj.device_info
    device_info_short.short_description = 'Device Info'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


# Customize admin site headers
admin.site.site_header = 'Sushrusa Healthcare Platform Admin'
admin.site.site_title = 'Sushrusa Admin'
admin.site.index_title = 'Welcome to Sushrusa Administration'

