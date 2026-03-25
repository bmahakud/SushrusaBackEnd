from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'type', 'title', 'category', 'is_read', 'action_required', 'created_at']
    list_filter = ['type', 'category', 'is_read', 'action_required', 'created_at']
    search_fields = ['title', 'message']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 50
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('type', 'title', 'message', 'category')
        }),
        ('Status', {
            'fields': ('is_read', 'action_required')
        }),
        ('Actions', {
            'fields': ('action_url', 'metadata')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_read', 'mark_as_unread', 'mark_action_required', 'mark_action_not_required']
    
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} notifications marked as read.')
    mark_as_read.short_description = "Mark selected notifications as read"
    
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} notifications marked as unread.')
    mark_as_unread.short_description = "Mark selected notifications as unread"
    
    def mark_action_required(self, request, queryset):
        updated = queryset.update(action_required=True)
        self.message_user(request, f'{updated} notifications marked as requiring action.')
    mark_action_required.short_description = "Mark selected notifications as requiring action"
    
    def mark_action_not_required(self, request, queryset):
        updated = queryset.update(action_required=False)
        self.message_user(request, f'{updated} notifications marked as not requiring action.')
    mark_action_not_required.short_description = "Mark selected notifications as not requiring action" 