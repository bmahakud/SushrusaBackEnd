from django.core.management.base import BaseCommand
from authentication.models import User
from patients.models import PatientProfile
from doctors.models import DoctorProfile

class Command(BaseCommand):
    help = 'Create missing PatientProfile and DoctorProfile objects for users with the respective roles.'

    def handle(self, *args, **options):
        created_patients = 0
        created_doctors = 0
        # Create missing PatientProfiles
        for user in User.objects.filter(role='patient'):
            if not PatientProfile.objects.filter(user=user).exists():
                PatientProfile.objects.create(user=user)
                self.stdout.write(f'Created PatientProfile for {user.phone}')
                created_patients += 1
        # Create missing DoctorProfiles
        for user in User.objects.filter(role='doctor'):
            if not DoctorProfile.objects.filter(user=user).exists():
                DoctorProfile.objects.create(
                    user=user,
                    license_number='TEMP',
                    qualification='MBBS',
                    specialization='General',
                    experience_years=0,
                    consultation_fee=0,
                    languages_spoken=[],
                    is_verified=False,
                    is_active=True,
                    is_accepting_patients=True,
                    rating=0,
                    total_reviews=0
                )
                self.stdout.write(f'Created DoctorProfile for {user.phone}')
                created_doctors += 1
        self.stdout.write(self.style.SUCCESS(f'Created {created_patients} PatientProfiles and {created_doctors} DoctorProfiles.')) 