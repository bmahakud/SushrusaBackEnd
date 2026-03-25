from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('critical', 'Critical'),
        ('important', 'Important'),
        ('info', 'Info'),
        ('success', 'Success'),
    ]
    
    NOTIFICATION_CATEGORIES = [
        ('system', 'System'),
        ('doctors', 'Doctors'),
        ('clinics', 'Clinics'),
        ('payments', 'Payments'),
        ('analytics', 'Analytics'),
        ('security', 'Security'),
    ]
    
    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='info')
    title = models.CharField(max_length=200)
    message = models.TextField()
    category = models.CharField(max_length=20, choices=NOTIFICATION_CATEGORIES, default='system')
    is_read = models.BooleanField(default=False)
    action_required = models.BooleanField(default=False)
    action_url = models.URLField(blank=True, null=True)
    
    # Metadata for additional context
    metadata = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
    
    def __str__(self):
        return f"{self.type.upper()}: {self.title}"
    
    @property
    def timestamp(self):
        return self.created_at.isoformat()
    
    def mark_as_read(self):
        self.is_read = True
        self.save(update_fields=['is_read', 'updated_at'])
    
    @classmethod
    def create_notification(cls, type, title, message, category='system', action_required=False, action_url=None, metadata=None):
        """Helper method to create notifications"""
        return cls.objects.create(
            type=type,
            title=title,
            message=message,
            category=category,
            action_required=action_required,
            action_url=action_url,
            metadata=metadata or {}
        )
    
    @classmethod
    def get_unread_count(cls):
        """Get count of unread notifications"""
        return cls.objects.filter(is_read=False).count()
    
    @classmethod
    def get_critical_count(cls):
        """Get count of critical notifications"""
        return cls.objects.filter(type='critical', is_read=False).count()
    
    @classmethod
    def get_action_required_count(cls):
        """Get count of notifications requiring action"""
        return cls.objects.filter(action_required=True, is_read=False).count() 