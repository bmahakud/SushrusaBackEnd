from django.core.management.base import BaseCommand
from authentication.models import User
from eclinic.models import Clinic

class Command(BaseCommand):
    help = 'Create 12 sample e-clinics, each assigned to a different admin and set as verified.'

    def handle(self, *args, **options):
        cities = ['Bhubaneswar', 'Cuttack', 'Puri', 'Sambalpur', 'Rourkela', 'Berhampur', 'Balasore', 'Baripada', 'Jharsuguda', 'Angul', 'Dhenkanal', 'Paradeep']
        admins = list(User.objects.filter(role='admin'))
        if not admins:
            self.stdout.write(self.style.ERROR('No admin users found!'))
            return
        for i, city in enumerate(cities):
            admin = admins[i % len(admins)]
            reg_num = f'REG20250{i:02d}'
            clinic, created = Clinic.objects.get_or_create(
                registration_number=reg_num,
                defaults={
                    'name': f'{city} Digital Clinic',
                    'clinic_type': 'virtual_clinic',
                    'description': f'A modern e-clinic in {city}',
                    'phone': f'+9198765432{i:02d}',
                    'email': f'{city.lower()}clinic@example.com',
                    'website': f'https://{city.lower()}clinic.com',
                    'street': f'Plot {100+i}, Main Road',
                    'city': city,
                    'state': 'Odisha',
                    'pincode': f'75{i:03d}',
                    'country': 'India',
                    'latitude': 20.0 + i,
                    'longitude': 85.0 + i,
                    'operating_hours': {'monday': {'start': '09:00', 'end': '18:00'}},
                    'specialties': ['General Medicine', 'Pediatrics'],
                    'services': ['Consultation', 'Telemedicine'],
                    'facilities': ['Video Call', 'Pharmacy'],
                    'license_number': f'LIC20250{i:02d}',
                    'accreditation': 'NABH',
                    'is_active': True,
                    'is_verified': True,
                    'accepts_online_consultations': True,
                    'admin': admin
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created {clinic.name} assigned to {admin.name}'))
            else:
                self.stdout.write(f'{clinic.name} (registration_number={reg_num}) already exists.') 