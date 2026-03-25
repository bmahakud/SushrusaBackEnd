from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from patients.models import PatientProfile
from datetime import date

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a patient account with the given phone number'

    def add_arguments(self, parser):
        parser.add_argument('phone', type=str, help='Patient phone number')
        parser.add_argument('--name', type=str, default='Test Patient', help='Patient name')
        parser.add_argument('--email', type=str, default='patient@example.com', help='Patient email')

    def handle(self, *args, **options):
        phone = options['phone']
        name = options['name']
        email = options['email']

        try:
            # Check if user already exists
            if User.objects.filter(phone=phone).exists():
                self.stdout.write(
                    self.style.WARNING(f'User with phone {phone} already exists')
                )
                return

            # Create user
            user = User.objects.create_user(
                phone=phone,
                name=name,
                email=email,
                role='patient',
                date_of_birth=date(1990, 1, 1),
                gender='male',
                street='123 Test Street',
                city='Mumbai',
                state='Maharashtra',
                pincode='400001',
                country='India',
                emergency_contact_name='Emergency Contact',
                emergency_contact_phone='9876543210',
                emergency_contact_relationship='Spouse',
                blood_group='O+',
                allergies='None',
                medical_history='No significant medical history'
            )

            # Create patient profile
            patient_profile = PatientProfile.objects.create(
                user=user,
                blood_group='O+',
                allergies='None',
                chronic_conditions=[],
                current_medications=[],
                insurance_provider='Test Insurance',
                insurance_policy_number='TI123456789',
                insurance_expiry=date(2025, 12, 31),
                preferred_language='english'
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created patient account:\n'
                    f'- Name: {user.name}\n'
                    f'- Phone: {user.phone}\n'
                    f'- Email: {user.email}\n'
                    f'- Role: {user.role}\n'
                    f'- Patient Profile ID: {patient_profile.id}'
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating patient account: {str(e)}')
            )
