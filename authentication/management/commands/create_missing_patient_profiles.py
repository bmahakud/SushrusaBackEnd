from django.core.management.base import BaseCommand
from authentication.models import User
from patients.models import PatientProfile


class Command(BaseCommand):
    help = 'Create missing patient profiles for users with patient role'

    def add_arguments(self, parser):
        parser.add_argument('--phone', type=str, help='Specific phone number to create profile for')
        parser.add_argument('--all', action='store_true', help='Create profiles for all missing patients')

    def handle(self, *args, **options):
        if options['phone']:
            # Create profile for specific phone number
            try:
                user = User.objects.get(phone=options['phone'])
                if user.role != 'patient':
                    self.stdout.write(
                        self.style.ERROR(f'User {user.phone} is not a patient (role: {user.role})')
                    )
                    return
                
                if PatientProfile.objects.filter(user=user).exists():
                    self.stdout.write(
                        self.style.WARNING(f'Patient profile already exists for {user.phone}')
                    )
                    return
                
                profile = PatientProfile.objects.create(
                    user=user,
                    blood_group='O+',
                    allergies='None',
                    chronic_conditions=[],
                    current_medications=[],
                    insurance_provider='',
                    insurance_policy_number='',
                    insurance_expiry=None,
                    preferred_language='english'
                )
                
                self.stdout.write(
                    self.style.SUCCESS(f'Created patient profile for {user.phone} (User: {user.name})')
                )
                self.stdout.write(f'Profile ID: {profile.id}')
                
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'User with phone {options["phone"]} not found')
                )
        
        elif options['all']:
            # Create profiles for all missing patients
            patients_without_profiles = User.objects.filter(
                role='patient'
            ).exclude(
                id__in=PatientProfile.objects.values_list('user_id', flat=True)
            )
            
            created_count = 0
            for user in patients_without_profiles:
                profile = PatientProfile.objects.create(
                    user=user,
                    blood_group='O+',
                    allergies='None',
                    chronic_conditions=[],
                    current_medications=[],
                    insurance_provider='',
                    insurance_policy_number='',
                    insurance_expiry=None,
                    preferred_language='english'
                )
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created profile for {user.phone} (User: {user.name})')
                )
            
            self.stdout.write(
                self.style.SUCCESS(f'Created {created_count} patient profiles')
            )
        
        else:
            self.stdout.write(
                self.style.ERROR('Please specify --phone <number> or --all')
            ) 