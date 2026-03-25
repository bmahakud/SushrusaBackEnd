from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, time
from authentication.models import User
from doctors.models import DoctorSlot
from eclinic.models import Clinic


class Command(BaseCommand):
    help = 'Test the new slot-based consultation system'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Testing slot-based consultation system...'))
        
        # Get or create test data
        try:
            # Get first doctor
            doctor = User.objects.filter(role='doctor').first()
            if not doctor:
                self.stdout.write(self.style.ERROR('No doctor found. Please create a doctor first.'))
                return
            
            # Get first clinic
            clinic = Clinic.objects.first()
            if not clinic:
                self.stdout.write(self.style.ERROR('No clinic found. Please create a clinic first.'))
                return
            
            # Set consultation duration if not set
            if not clinic.consultation_duration:
                clinic.consultation_duration = 15
                clinic.save()
                self.stdout.write(f'Set consultation duration to {clinic.consultation_duration} minutes for clinic {clinic.name}')
            
            # Test date (tomorrow)
            test_date = timezone.now().date() + timezone.timedelta(days=1)
            start_time = time(10, 0)  # 10:00 AM
            end_time = time(12, 0)    # 12:00 PM
            
            self.stdout.write(f'Generating slots for Dr. {doctor.name} at {clinic.name}')
            self.stdout.write(f'Date: {test_date}, Time: {start_time} - {end_time}')
            self.stdout.write(f'Consultation duration: {clinic.consultation_duration} minutes')
            
            # Generate slots
            slots = DoctorSlot.generate_slots_for_availability(
                doctor=doctor,
                clinic=clinic,
                date=test_date,
                start_time=start_time,
                end_time=end_time
            )
            
            self.stdout.write(self.style.SUCCESS(f'Successfully generated {len(slots)} slots:'))
            for slot in slots:
                self.stdout.write(f'  - {slot.start_time} - {slot.end_time} (Available: {slot.is_available}, Booked: {slot.is_booked})')
            
            # Test available slots API
            available_slots = DoctorSlot.objects.filter(
                doctor=doctor,
                clinic=clinic,
                date=test_date,
                is_available=True,
                is_booked=False
            ).order_by('start_time')
            
            self.stdout.write(f'\nAvailable slots: {available_slots.count()}')
            for slot in available_slots:
                self.stdout.write(f'  - {slot.start_time} - {slot.end_time}')
            
            self.stdout.write(self.style.SUCCESS('\nSlot system test completed successfully!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error testing slot system: {e}')) 