from django.core.management.base import BaseCommand
from authentication.models import User
from eclinic.models import Clinic

class Command(BaseCommand):
    help = 'Delete all e-clinics and recreate one e-clinic per admin, assigning each admin to only one unique clinic.'

    def handle(self, *args, **options):
        # Delete all clinics
        Clinic.objects.all().delete()
        self.stdout.write(self.style.WARNING('Deleted all existing e-clinics.'))

        # Create one clinic per admin
        admins = User.objects.filter(role='admin')
        for i, admin in enumerate(admins):
            city = f'City{i+1}'
            clinic = Clinic.objects.create(
                name=f'{city} Digital Clinic',
                clinic_type='virtual_clinic',
                description=f'A modern e-clinic in {city}',
                phone=f'+9198765432{i:02d}',
                email=f'{city.lower()}clinic@example.com',
                website=f'https://{city.lower()}clinic.com',
                street=f'Plot {100+i}, Main Road',
                city=city,
                state='Odisha',
                pincode=f'75{i:03d}',
                country='India',
                latitude=20.0 + i,
                longitude=85.0 + i,
                operating_hours={'monday': {'start': '09:00', 'end': '18:00'}},
                specialties=['General Medicine', 'Pediatrics'],
                services=['Consultation', 'Telemedicine'],
                facilities=['Video Call', 'Pharmacy'],
                registration_number=f'REG20250{i:02d}',
                license_number=f'LIC20250{i:02d}',
                accreditation='NABH',
                is_active=True,
                is_verified=True,
                accepts_online_consultations=True,
                admin=admin
            )
            self.stdout.write(self.style.SUCCESS(f'Created {clinic.name} assigned to {admin.name}')) 