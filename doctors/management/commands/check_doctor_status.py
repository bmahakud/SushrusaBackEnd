from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from doctors.models import DoctorStatus


class Command(BaseCommand):
    help = 'Check current doctor status and activity'

    def add_arguments(self, parser):
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Show detailed information for each doctor'
        )

    def handle(self, *args, **options):
        detailed = options['detailed']
        
        # Get counts
        total_doctors = DoctorStatus.objects.count()
        online_doctors = DoctorStatus.objects.filter(is_online=True).count()
        offline_doctors = DoctorStatus.objects.filter(is_online=False).count()
        
        # Get recent activity (last 10 minutes)
        recent_threshold = timezone.now() - timedelta(minutes=10)
        recent_activity = DoctorStatus.objects.filter(
            last_activity__gte=recent_threshold
        ).count()
        
        self.stdout.write('='*60)
        self.stdout.write('DOCTOR STATUS SUMMARY')
        self.stdout.write('='*60)
        self.stdout.write(f'Total Doctors: {total_doctors}')
        self.stdout.write(f'Online Doctors: {online_doctors}')
        self.stdout.write(f'Offline Doctors: {offline_doctors}')
        self.stdout.write(f'Recent Activity (last 10 min): {recent_activity}')
        self.stdout.write('='*60)
        
        if detailed:
            self.stdout.write('\nDETAILED STATUS:')
            self.stdout.write('-'*60)
            
            for status in DoctorStatus.objects.all().order_by('-last_activity'):
                doctor_name = status.doctor.user.name
                current_status = status.current_status
                is_online = status.is_online
                last_activity = status.last_activity.strftime('%H:%M:%S')
                
                status_icon = '🟢' if is_online else '🔴'
                
                self.stdout.write(
                    f'{status_icon} {doctor_name:<30} | '
                    f'Status: {current_status:<12} | '
                    f'Online: {str(is_online):<5} | '
                    f'Last Activity: {last_activity}'
                )
        
        # Check for potential issues
        if online_doctors > 0:
            self.stdout.write('\n⚠️  ONLINE DOCTORS:')
            for status in DoctorStatus.objects.filter(is_online=True):
                time_since_activity = timezone.now() - status.last_activity
                minutes = int(time_since_activity.total_seconds() / 60)
                
                if minutes > 5:
                    self.stdout.write(
                        f'  ⚠️  {status.doctor.user.name} - '
                        f'Last activity: {minutes} minutes ago'
                    )
        
        self.stdout.write('\n' + '='*60) 