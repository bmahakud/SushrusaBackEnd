from django.core.management.base import BaseCommand
from doctors.models import DoctorStatus
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Make all doctors offline by updating their status'

    def handle(self, *args, **options):
        try:
            # Get all online doctors
            online_doctors = DoctorStatus.objects.filter(is_online=True)
            
            if not online_doctors.exists():
                self.stdout.write(
                    self.style.SUCCESS('✅ No doctors are currently online')
                )
                return
            
            # Update all online doctors to offline
            current_time = timezone.now()
            updated_count = online_doctors.update(
                is_online=False,
                is_logged_in=False,
                current_status='offline',
                last_activity=current_time,
                status_updated_at=current_time,
                status_note='Marked offline by admin command'
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Successfully made {updated_count} doctors offline'
                )
            )
            
            # Show which doctors were made offline
            self.stdout.write('\n📋 Doctors made offline:')
            for doctor in online_doctors:
                self.stdout.write(f'  • {doctor.doctor_name} (ID: {doctor.doctor_id})')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error making doctors offline: {e}')
            )
            logger.error(f'Error in make_all_doctors_offline command: {e}') 