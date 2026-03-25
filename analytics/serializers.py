from rest_framework import serializers
from django.utils import timezone
from .models import (
    UserAnalytics, RevenueAnalytics, DoctorPerformanceAnalytics,
    PlatformMetrics, SystemPerformanceMetrics
)


class UserAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for user analytics"""
    
    class Meta:
        model = UserAnalytics
        fields = [
            'id', 'date', 'new_patients', 'new_doctors', 'total_users',
            'active_patients', 'active_doctors', 'avg_session_duration',
            'total_sessions', 'top_cities', 'top_states', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class RevenueAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for revenue analytics"""
    
    class Meta:
        model = RevenueAnalytics
        fields = [
            'id', 'date', 'total_revenue', 'consultation_revenue',
            'platform_fee_revenue', 'successful_payments', 'failed_payments',
            'refunded_amount', 'card_payments', 'upi_payments',
            'wallet_payments', 'cash_payments', 'avg_consultation_fee',
            'avg_transaction_value', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class DoctorPerformanceSerializer(serializers.ModelSerializer):
    """Serializer for doctor performance"""
    doctor_name = serializers.CharField(source='doctor.name', read_only=True)
    
    class Meta:
        model = DoctorPerformanceAnalytics
        fields = [
            'id', 'doctor', 'doctor_name', 'date', 'total_consultations',
            'completed_consultations', 'cancelled_consultations',
            'avg_rating', 'total_revenue', 'avg_consultation_fee',
            'total_reviews', 'avg_consultation_duration', 'on_time_percentage',
            'new_patients', 'returning_patients', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class PlatformMetricsSerializer(serializers.ModelSerializer):
    """Serializer for platform metrics"""
    
    class Meta:
        model = PlatformMetrics
        fields = [
            'id', 'date', 'total_registered_users', 'total_active_users',
            'total_patients', 'total_doctors', 'total_consultations_completed',
            'consultation_completion_rate', 'total_platform_revenue',
            'monthly_recurring_revenue', 'user_growth_rate', 'revenue_growth_rate',
            'avg_consultations_per_user', 'user_retention_rate',
            'avg_platform_rating', 'customer_satisfaction_score', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class SystemPerformanceMetricsSerializer(serializers.ModelSerializer):
    """Serializer for system performance metrics"""
    
    class Meta:
        model = SystemPerformanceMetrics
        fields = [
            'id', 'date', 'avg_response_time', 'total_api_calls', 'failed_api_calls',
            'avg_db_query_time', 'total_db_queries', 'slow_queries',
            'total_errors', 'critical_errors', 'error_rate', 'page_load_time',
            'bounce_rate', 'cpu_usage', 'memory_usage', 'disk_usage', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for dashboard statistics"""
    total_users = serializers.IntegerField()
    total_patients = serializers.IntegerField()
    total_doctors = serializers.IntegerField()
    total_consultations = serializers.IntegerField()
    total_prescriptions = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
    active_users_today = serializers.IntegerField()
    consultations_today = serializers.IntegerField()
    revenue_today = serializers.DecimalField(max_digits=10, decimal_places=2)
    growth_metrics = serializers.DictField()


class UserGrowthSerializer(serializers.Serializer):
    """Serializer for user growth analytics"""
    period = serializers.CharField()
    total_users = serializers.IntegerField()
    new_users = serializers.IntegerField()
    growth_rate = serializers.FloatField()
    user_type_breakdown = serializers.DictField()


class RevenueReportSerializer(serializers.Serializer):
    """Serializer for revenue reports"""
    period = serializers.CharField()
    total_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
    revenue_breakdown = serializers.DictField()
    growth_rate = serializers.FloatField()
    top_revenue_sources = serializers.ListField()


class ConsultationAnalyticsSerializer(serializers.Serializer):
    """Serializer for consultation analytics"""
    total_consultations = serializers.IntegerField()
    completed_consultations = serializers.IntegerField()
    cancelled_consultations = serializers.IntegerField()
    average_duration = serializers.FloatField()
    consultation_types = serializers.DictField()
    peak_hours = serializers.ListField()
    doctor_performance = serializers.ListField()


class GeographicAnalyticsSerializer(serializers.Serializer):
    """Serializer for geographic analytics"""
    user_distribution = serializers.DictField()
    consultation_distribution = serializers.DictField()
    revenue_distribution = serializers.DictField()
    top_cities = serializers.ListField()
    growth_by_region = serializers.DictField()


class PerformanceMetricsSerializer(serializers.Serializer):
    """Serializer for performance metrics"""
    api_response_time = serializers.FloatField()
    database_query_time = serializers.FloatField()
    error_rate = serializers.FloatField()
    uptime_percentage = serializers.FloatField()
    concurrent_users = serializers.IntegerField()
    system_load = serializers.DictField()


class CustomReportSerializer(serializers.Serializer):
    """Serializer for custom report generation"""
    report_type = serializers.ChoiceField(choices=[
        ('user_growth', 'User Growth'),
        ('revenue', 'Revenue Analysis'),
        ('consultation', 'Consultation Analytics'),
        ('doctor_performance', 'Doctor Performance'),
        ('patient_engagement', 'Patient Engagement'),
        ('geographic', 'Geographic Analysis'),
        ('performance', 'Performance Metrics')
    ])
    date_from = serializers.DateField()
    date_to = serializers.DateField()
    filters = serializers.JSONField(required=False)
    group_by = serializers.ChoiceField(
        choices=[('day', 'Daily'), ('week', 'Weekly'), ('month', 'Monthly')],
        default='day'
    )
    
    def validate(self, attrs):
        """Validate report parameters"""
        date_from = attrs.get('date_from')
        date_to = attrs.get('date_to')
        
        if date_from and date_to and date_from > date_to:
            raise serializers.ValidationError('date_from cannot be greater than date_to')
        
        # Check date range (max 1 year)
        if date_from and date_to:
            delta = date_to - date_from
            if delta.days > 365:
                raise serializers.ValidationError('Date range cannot exceed 1 year')
        
        return attrs


class ExportRequestSerializer(serializers.Serializer):
    """Serializer for data export requests"""
    export_type = serializers.ChoiceField(choices=[
        ('users', 'Users'),
        ('consultations', 'Consultations'),
        ('prescriptions', 'Prescriptions'),
        ('payments', 'Payments'),
        ('analytics', 'Analytics')
    ])
    format = serializers.ChoiceField(choices=[
        ('csv', 'CSV'),
        ('excel', 'Excel'),
        ('pdf', 'PDF')
    ])
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    filters = serializers.JSONField(required=False)
    
    def validate(self, attrs):
        """Validate export parameters"""
        date_from = attrs.get('date_from')
        date_to = attrs.get('date_to')
        
        if date_from and date_to and date_from > date_to:
            raise serializers.ValidationError('date_from cannot be greater than date_to')
        
        return attrs


class AlertConfigSerializer(serializers.Serializer):
    """Serializer for analytics alerts configuration"""
    alert_type = serializers.ChoiceField(choices=[
        ('user_growth', 'User Growth'),
        ('revenue_drop', 'Revenue Drop'),
        ('error_rate', 'Error Rate'),
        ('system_health', 'System Health'),
        ('consultation_volume', 'Consultation Volume')
    ])
    threshold = serializers.FloatField()
    condition = serializers.ChoiceField(choices=[
        ('greater_than', 'Greater Than'),
        ('less_than', 'Less Than'),
        ('equals', 'Equals')
    ])
    notification_channels = serializers.ListField(
        child=serializers.ChoiceField(choices=[
            ('email', 'Email'),
            ('sms', 'SMS'),
            ('slack', 'Slack'),
            ('webhook', 'Webhook')
        ])
    )
    is_active = serializers.BooleanField(default=True)


class RealTimeMetricsSerializer(serializers.Serializer):
    """Serializer for real-time metrics"""
    active_users = serializers.IntegerField()
    ongoing_consultations = serializers.IntegerField()
    pending_payments = serializers.IntegerField()
    system_status = serializers.CharField()
    api_calls_per_minute = serializers.IntegerField()
    error_rate_last_hour = serializers.FloatField()
    database_connections = serializers.IntegerField()
    queue_size = serializers.IntegerField()
    timestamp = serializers.DateTimeField()



