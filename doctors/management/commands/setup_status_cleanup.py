from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from doctors.models import DoctorStatus


class Command(BaseCommand):
    help = 'Set up automatic doctor status cleanup'

    def add_arguments(self, parser):
        parser.add_argument(
            '--minutes',
            type=int,
            default=5,
            help='Number of minutes of inactivity before marking as offline (default: 5)'
        )

    def handle(self, *args, **options):
        minutes = options['minutes']
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Setting up automatic cleanup for doctors inactive for more than {minutes} minutes'
            )
        )
        
        # Mark currently inactive doctors as offline
        inactive_threshold = timezone.now() - timedelta(minutes=minutes)
        inactive_doctors = DoctorStatus.objects.filter(
            is_online=True,
            last_activity__lt=inactive_threshold
        )
        
        count = 0
        for doctor_status in inactive_doctors:
            doctor_status.is_online = False
            doctor_status.is_logged_in = False
            doctor_status.current_status = 'offline'
            doctor_status.save()
            count += 1
            
            self.stdout.write(
                f'  - Marked {doctor_status.doctor.user.name} as offline'
            )
        
        if count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully marked {count} doctors as offline'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    'No inactive doctors found'
                )
            )
        
        # Instructions for setting up cron job
        self.stdout.write('\n' + '='*60)
        self.stdout.write('TO SET UP AUTOMATIC CLEANUP:')
        self.stdout.write('='*60)
        self.stdout.write('1. Open crontab: crontab -e')
        self.stdout.write('2. Add this line to run every 5 minutes:')
        self.stdout.write(f'   */5 * * * * cd /path/to/your/project && python manage.py mark_inactive_doctors_offline --minutes {minutes}')
        self.stdout.write('3. Save and exit')
        self.stdout.write('4. Verify with: crontab -l')
        self.stdout.write('='*60) 