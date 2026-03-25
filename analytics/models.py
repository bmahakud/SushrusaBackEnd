from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal


class UserAnalytics(models.Model):
    """Daily user analytics data"""
    
    date = models.DateField()
    
    # User Registration
    new_patients = models.PositiveIntegerField(default=0)
    new_doctors = models.PositiveIntegerField(default=0)
    total_users = models.PositiveIntegerField(default=0)
    
    # User Activity
    active_patients = models.PositiveIntegerField(default=0)
    active_doctors = models.PositiveIntegerField(default=0)
    
    # User Engagement
    avg_session_duration = models.DurationField(null=True, blank=True)
    total_sessions = models.PositiveIntegerField(default=0)
    
    # Geographic Data
    top_cities = models.JSONField(default=list, help_text="Top cities by user count")
    top_states = models.JSONField(default=list, help_text="Top states by user count")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_analytics'
        verbose_name = 'User Analytics'
        verbose_name_plural = 'User Analytics'
        unique_together = ['date']
        ordering = ['-date']
    
    def __str__(self):
        return f"User Analytics - {self.date}"


class ConsultationAnalytics(models.Model):
    """Daily consultation analytics data"""
    
    date = models.DateField()
    
    # Consultation Counts
    total_consultations = models.PositiveIntegerField(default=0)
    completed_consultations = models.PositiveIntegerField(default=0)
    cancelled_consultations = models.PositiveIntegerField(default=0)
    no_show_consultations = models.PositiveIntegerField(default=0)
    
    # Consultation Types
    in_person_consultations = models.PositiveIntegerField(default=0)
    video_consultations = models.PositiveIntegerField(default=0)
    phone_consultations = models.PositiveIntegerField(default=0)
    
    # Timing Analytics
    avg_consultation_duration = models.DurationField(null=True, blank=True)
    avg_wait_time = models.DurationField(null=True, blank=True)
    
    # Specialty Breakdown
    specialty_breakdown = models.JSONField(default=dict, help_text="Consultations by specialty")
    
    # Peak Hours
    peak_hours = models.JSONField(default=list, help_text="Peak consultation hours")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'consultation_analytics'
        verbose_name = 'Consultation Analytics'
        verbose_name_plural = 'Consultation Analytics'
        unique_together = ['date']
        ordering = ['-date']
    
    def __str__(self):
        return f"Consultation Analytics - {self.date}"


class RevenueAnalytics(models.Model):
    """Daily revenue analytics data"""
    
    date = models.DateField()
    
    # Revenue Metrics
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    consultation_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    platform_fee_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Payment Analytics
    successful_payments = models.PositiveIntegerField(default=0)
    failed_payments = models.PositiveIntegerField(default=0)
    refunded_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Payment Method Breakdown
    card_payments = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    upi_payments = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    wallet_payments = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    cash_payments = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Average Metrics
    avg_consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    avg_transaction_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'revenue_analytics'
        verbose_name = 'Revenue Analytics'
        verbose_name_plural = 'Revenue Analytics'
        unique_together = ['date']
        ordering = ['-date']
    
    def __str__(self):
        return f"Revenue Analytics - {self.date} - ₹{self.total_revenue}"


class DoctorPerformanceAnalytics(models.Model):
    """Doctor performance analytics"""
    
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='performance_analytics'
    )
    date = models.DateField()
    
    # Consultation Metrics
    total_consultations = models.PositiveIntegerField(default=0)
    completed_consultations = models.PositiveIntegerField(default=0)
    cancelled_consultations = models.PositiveIntegerField(default=0)
    no_show_consultations = models.PositiveIntegerField(default=0)
    
    # Revenue Metrics
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    avg_consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Rating and Reviews
    avg_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_reviews = models.PositiveIntegerField(default=0)
    
    # Efficiency Metrics
    avg_consultation_duration = models.DurationField(null=True, blank=True)
    on_time_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Patient Metrics
    new_patients = models.PositiveIntegerField(default=0)
    returning_patients = models.PositiveIntegerField(default=0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'doctor_performance_analytics'
        verbose_name = 'Doctor Performance Analytics'
        verbose_name_plural = 'Doctor Performance Analytics'
        unique_together = ['doctor', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"Dr. {self.doctor.name} Performance - {self.date}"


class ClinicPerformanceAnalytics(models.Model):
    """Clinic performance analytics"""
    
    clinic = models.ForeignKey(
        'eclinic.Clinic', 
        on_delete=models.CASCADE, 
        related_name='performance_analytics'
    )
    date = models.DateField()
    
    # Consultation Metrics
    total_consultations = models.PositiveIntegerField(default=0)
    completed_consultations = models.PositiveIntegerField(default=0)
    cancelled_consultations = models.PositiveIntegerField(default=0)
    
    # Revenue Metrics
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    avg_consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Patient Metrics
    unique_patients = models.PositiveIntegerField(default=0)
    new_patients = models.PositiveIntegerField(default=0)
    returning_patients = models.PositiveIntegerField(default=0)
    
    # Doctor Metrics
    active_doctors = models.PositiveIntegerField(default=0)
    
    # Rating and Reviews
    avg_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_reviews = models.PositiveIntegerField(default=0)
    
    # Utilization Metrics
    room_utilization = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    doctor_utilization = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'clinic_performance_analytics'
        verbose_name = 'Clinic Performance Analytics'
        verbose_name_plural = 'Clinic Performance Analytics'
        unique_together = ['clinic', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.clinic.name} Performance - {self.date}"


class SystemPerformanceMetrics(models.Model):
    """System performance and technical metrics"""
    
    date = models.DateField()
    
    # API Performance
    avg_response_time = models.DecimalField(max_digits=8, decimal_places=3, default=0, help_text="Average response time in seconds")
    total_api_calls = models.PositiveIntegerField(default=0)
    failed_api_calls = models.PositiveIntegerField(default=0)
    
    # Database Performance
    avg_db_query_time = models.DecimalField(max_digits=8, decimal_places=3, default=0, help_text="Average DB query time in seconds")
    total_db_queries = models.PositiveIntegerField(default=0)
    slow_queries = models.PositiveIntegerField(default=0)
    
    # Error Tracking
    total_errors = models.PositiveIntegerField(default=0)
    critical_errors = models.PositiveIntegerField(default=0)
    error_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Error rate percentage")
    
    # User Experience
    page_load_time = models.DecimalField(max_digits=8, decimal_places=3, default=0, help_text="Average page load time in seconds")
    bounce_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Bounce rate percentage")
    
    # System Resources
    cpu_usage = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Average CPU usage percentage")
    memory_usage = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Average memory usage percentage")
    disk_usage = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Disk usage percentage")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'system_performance_metrics'
        verbose_name = 'System Performance Metrics'
        verbose_name_plural = 'System Performance Metrics'
        unique_together = ['date']
        ordering = ['-date']
    
    def __str__(self):
        return f"System Performance - {self.date}"


class UserActivityLog(models.Model):
    """Log user activities for analytics"""
    
    ACTIVITY_TYPES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('profile_update', 'Profile Update'),
        ('consultation_book', 'Consultation Booked'),
        ('consultation_cancel', 'Consultation Cancelled'),
        ('payment_made', 'Payment Made'),
        ('review_submitted', 'Review Submitted'),
        ('prescription_viewed', 'Prescription Viewed'),
        ('document_upload', 'Document Uploaded'),
        ('search', 'Search'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='activity_logs'
    )
    activity_type = models.CharField(max_length=30, choices=ACTIVITY_TYPES)
    description = models.CharField(max_length=500)
    
    # Context Data
    metadata = models.JSONField(default=dict, help_text="Additional context data")
    
    # Session Information
    session_id = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Location (if available)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    # Timestamp
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_activity_logs'
        verbose_name = 'User Activity Log'
        verbose_name_plural = 'User Activity Logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'activity_type']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.name} - {self.activity_type} - {self.timestamp}"


class PlatformMetrics(models.Model):
    """Overall platform metrics and KPIs"""
    
    date = models.DateField()
    
    # User Metrics
    total_registered_users = models.PositiveIntegerField(default=0)
    total_active_users = models.PositiveIntegerField(default=0)
    total_patients = models.PositiveIntegerField(default=0)
    total_doctors = models.PositiveIntegerField(default=0)
    
    # Consultation Metrics
    total_consultations_completed = models.PositiveIntegerField(default=0)
    consultation_completion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Revenue Metrics
    total_platform_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    monthly_recurring_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Growth Metrics
    user_growth_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    revenue_growth_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Engagement Metrics
    avg_consultations_per_user = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    user_retention_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Quality Metrics
    avg_platform_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    customer_satisfaction_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'platform_metrics'
        verbose_name = 'Platform Metrics'
        verbose_name_plural = 'Platform Metrics'
        unique_together = ['date']
        ordering = ['-date']
    
    def __str__(self):
        return f"Platform Metrics - {self.date}"

