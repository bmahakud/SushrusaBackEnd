from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from doctors.models import DoctorStatus


class Command(BaseCommand):
    help = 'Mark doctors as offline if they have been inactive for more than 5 minutes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--minutes',
            type=int,
            default=5,
            help='Number of minutes of inactivity before marking as offline (default: 5)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without actually doing it'
        )

    def handle(self, *args, **options):
        minutes = options['minutes']
        dry_run = options['dry_run']
        
        inactive_threshold = timezone.now() - timedelta(minutes=minutes)
        
        inactive_doctors = DoctorStatus.objects.filter(
            is_online=True,
            last_activity__lt=inactive_threshold
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'DRY RUN: Would mark {inactive_doctors.count()} doctors as offline'
                )
            )
            for doctor_status in inactive_doctors:
                self.stdout.write(
                    f'  - {doctor_status.doctor.user.name} (last active: {doctor_status.last_activity})'
                )
        else:
            count = 0
            for doctor_status in inactive_doctors:
                doctor_status.is_online = False
                doctor_status.is_logged_in = False
                doctor_status.current_status = 'offline'
                doctor_status.save()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Marked {doctor_status.doctor.user.name} as offline (last active: {doctor_status.last_activity})'
                    )
                )
                count += 1
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully marked {count} doctors as offline'
                )
            ) 