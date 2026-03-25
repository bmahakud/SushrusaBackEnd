from django.core.management.base import BaseCommand
from notifications.models import Notification
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Create sample notifications for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Number of sample notifications to create'
        )

    def handle(self, *args, **options):
        count = options['count']
        
        # Sample notifications data
        sample_notifications = [
            {
                'type': 'critical',
                'title': 'System Error Detected',
                'message': 'Database connection timeout occurred. System performance may be affected.',
                'category': 'system',
                'action_required': True,
                'metadata': {'errorCode': 'DB_001'}
            },
            {
                'type': 'important',
                'title': 'New Doctor Registration',
                'message': 'Dr. Sarah Johnson has registered and is pending verification.',
                'category': 'doctors',
                'action_required': True,
                'action_url': '/doctors/verify',
                'metadata': {'doctorId': 'DOC123'}
            },
            {
                'type': 'success',
                'title': 'Payment Processed Successfully',
                'message': 'Payment of ₹2,500 received for consultation ID CON456.',
                'category': 'payments',
                'action_required': False,
                'metadata': {'paymentId': 'PAY789', 'amount': 2500}
            },
            {
                'type': 'info',
                'title': 'High Traffic Alert',
                'message': 'Unusual traffic spike detected. Current load: 85% of capacity.',
                'category': 'analytics',
                'action_required': False
            },
            {
                'type': 'important',
                'title': 'New Clinic Registration',
                'message': 'City Medical Center has registered and requires approval.',
                'category': 'clinics',
                'action_required': True,
                'action_url': '/clinics/approve',
                'metadata': {'clinicId': 'CLINIC456'}
            },
            {
                'type': 'critical',
                'title': 'Security Alert',
                'message': 'Multiple failed login attempts detected from IP 192.168.1.100.',
                'category': 'security',
                'action_required': True,
                'metadata': {'ip': '192.168.1.100', 'attempts': 5}
            },
            {
                'type': 'success',
                'title': 'Doctor Verification Completed',
                'message': 'Dr. Michael Chen has been successfully verified and is now active.',
                'category': 'doctors',
                'action_required': False,
                'metadata': {'doctorId': 'DOC456'}
            },
            {
                'type': 'info',
                'title': 'System Maintenance Scheduled',
                'message': 'Scheduled maintenance will occur on Sunday at 2:00 AM. Expected downtime: 30 minutes.',
                'category': 'system',
                'action_required': False
            },
            {
                'type': 'important',
                'title': 'Payment Dispute Filed',
                'message': 'Payment dispute filed for consultation ID CON789. Amount: ₹1,500.',
                'category': 'payments',
                'action_required': True,
                'action_url': '/payments/disputes',
                'metadata': {'consultationId': 'CON789', 'amount': 1500}
            },
            {
                'type': 'success',
                'title': 'Revenue Milestone Reached',
                'message': 'Monthly revenue target of ₹50,000 has been achieved!',
                'category': 'analytics',
                'action_required': False,
                'metadata': {'target': 50000, 'achieved': 52000}
            }
        ]

        created_count = 0
        
        for i in range(min(count, len(sample_notifications))):
            notification_data = sample_notifications[i]
            
            # Create notification with staggered timestamps
            notification = Notification.objects.create(
                type=notification_data['type'],
                title=notification_data['title'],
                message=notification_data['message'],
                category=notification_data['category'],
                action_required=notification_data['action_required'],
                action_url=notification_data.get('action_url'),
                metadata=notification_data.get('metadata', {}),
                created_at=timezone.now() - timedelta(hours=i, minutes=i*5)
            )
            
            created_count += 1
            self.stdout.write(
                self.style.SUCCESS(f'Created notification: {notification.title}')
            )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} sample notifications')
        ) 