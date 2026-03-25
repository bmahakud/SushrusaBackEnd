from django.core.management.base import BaseCommand
from authentication.models import User
from patients.models import PatientProfile
from doctors.models import DoctorProfile


class Command(BaseCommand):
    help = 'Delete a user by phone number'

    def add_arguments(self, parser):
        parser.add_argument('phone', type=str, help='Phone number of the user to delete')

    def handle(self, *args, **options):
        phone = options['phone']
        
        try:
            user = User.objects.get(phone=phone)
            
            self.stdout.write(f'Found user: {user.name} ({user.phone})')
            self.stdout.write(f'Role: {user.role}')
            self.stdout.write(f'User ID: {user.id}')
            
            # Delete associated profiles based on role
            if user.role == 'patient':
                try:
                    profile = PatientProfile.objects.get(user=user)
                    self.stdout.write(f'Deleting patient profile ID: {profile.id}')
                    profile.delete()
                except PatientProfile.DoesNotExist:
                    self.stdout.write('No patient profile found')
            
            elif user.role == 'doctor':
                try:
                    profile = DoctorProfile.objects.get(user=user)
                    self.stdout.write(f'Deleting doctor profile ID: {profile.id}')
                    profile.delete()
                except DoctorProfile.DoesNotExist:
                    self.stdout.write('No doctor profile found')
            
            # Delete the user
            user.delete()
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully deleted user {phone}')
            )
            
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User with phone {phone} not found')
            ) 