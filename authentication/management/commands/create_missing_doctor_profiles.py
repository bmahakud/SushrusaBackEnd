from django.core.management.base import BaseCommand
from authentication.models import User
from doctors.models import DoctorProfile


class Command(BaseCommand):
    help = 'Create missing doctor profiles for existing doctor users'

    def add_arguments(self, parser):
        parser.add_argument('--phone', type=str, help='Specific phone number to create profile for')
        parser.add_argument('--all', action='store_true', help='Create profiles for all missing doctors')

    def handle(self, *args, **options):
        if options['phone']:
            # Create profile for specific phone number
            try:
                user = User.objects.get(phone=options['phone'])
                if user.role != 'doctor':
                    self.stdout.write(
                        self.style.ERROR(f'User {user.phone} is not a doctor (role: {user.role})')
                    )
                    return
                
                if DoctorProfile.objects.filter(user=user).exists():
                    self.stdout.write(
                        self.style.WARNING(f'Doctor profile already exists for {user.phone}')
                    )
                    return
                
                profile = DoctorProfile.objects.create(
                    user=user,
                    license_number=f'DOC{user.phone[-6:]}',
                    qualification='MBBS, MD',
                    specialization='general_medicine',
                    sub_specialization='',
                    experience_years=5,
                    consultation_fee=1500.00,
                    online_consultation_fee=1200.00,
                    languages_spoken=['English', 'Hindi'],
                    bio=f'Experienced doctor - {user.name}',
                    achievements='',
                    is_verified=True,
                    consultation_duration=5,
                    is_online_consultation_available=True,
                    is_active=True,
                    rating=0.0,
                    total_reviews=0,
                    clinic_name=f'{user.name} Clinic',
                    clinic_address='Medical Center',
                    is_accepting_patients=True
                )
                
                self.stdout.write(
                    self.style.SUCCESS(f'Created doctor profile for {user.phone} (User: {user.name})')
                )
                self.stdout.write(f'Profile ID: {profile.id}')
                
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'User with phone {options["phone"]} not found')
                )
        
        elif options['all']:
            # Create profiles for all missing doctors
            doctors_without_profiles = User.objects.filter(
                role='doctor'
            ).exclude(
                id__in=DoctorProfile.objects.values_list('user_id', flat=True)
            )
            
            created_count = 0
            for user in doctors_without_profiles:
                profile = DoctorProfile.objects.create(
                    user=user,
                    license_number=f'DOC{user.phone[-6:]}',
                    qualification='MBBS, MD',
                    specialization='general_medicine',
                    sub_specialization='',
                    experience_years=5,
                    consultation_fee=1500.00,
                    online_consultation_fee=1200.00,
                    languages_spoken=['English', 'Hindi'],
                    bio=f'Experienced doctor - {user.name}',
                    achievements='',
                    is_verified=True,
                    consultation_duration=5,
                    is_online_consultation_available=True,
                    is_active=True,
                    rating=0.0,
                    total_reviews=0,
                    clinic_name=f'{user.name} Clinic',
                    clinic_address='Medical Center',
                    is_accepting_patients=True
                )
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created profile for {user.phone} (User: {user.name})')
                )
            
            self.stdout.write(
                self.style.SUCCESS(f'Created {created_count} doctor profiles')
            )
        
        else:
            self.stdout.write(
                self.style.ERROR('Please specify --phone <number> or --all')
            ) 