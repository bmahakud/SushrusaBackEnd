from django.core.management.base import BaseCommand
from doctors.models import DoctorProfile, DoctorStatus
from django.utils import timezone

class Command(BaseCommand):
    help = 'Create DoctorStatus records for all existing doctors'

    def handle(self, *args, **options):
        doctors = DoctorProfile.objects.all()
        created_count = 0
        updated_count = 0
        
        for doctor in doctors:
            status, created = DoctorStatus.objects.get_or_create(
                doctor=doctor,
                defaults={
                    'is_online': False,
                    'is_logged_in': False,
                    'is_available': True,
                    'current_status': 'offline',
                    'last_activity': timezone.now(),
                    'status_updated_at': timezone.now(),
                    'status_note': '',
                    'auto_away_threshold': 15,
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created status for Dr. {doctor.user.name}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Status already exists for Dr. {doctor.user.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully processed {len(doctors)} doctors. '
                f'Created: {created_count}, Updated: {updated_count}'
            )
        ) 