from django.core.management.base import BaseCommand
from authentication.models import User
from eclinic.models import Clinic

class Command(BaseCommand):
    help = 'Create 10 verified eclinics in Odisha, each assigned to a unique available admin.'

    def handle(self, *args, **options):
        cities = [
            'Bhubaneswar', 'Cuttack', 'Puri', 'Sambalpur', 'Rourkela',
            'Berhampur', 'Balasore', 'Baripada', 'Jharsuguda', 'Angul',
        ]
        # Get admins who are not already assigned to a clinic
        assigned_admin_ids = Clinic.objects.values_list('admin_id', flat=True)
        available_admins = User.objects.filter(role='admin', is_verified=True).exclude(id__in=assigned_admin_ids)[:10]
        if available_admins.count() < 10:
            self.stdout.write(self.style.WARNING(f'Only {available_admins.count()} available admins found. Creating {available_admins.count()} clinics.'))
        for i, admin in enumerate(available_admins):
            city = cities[i % len(cities)]
            clinic = Clinic.objects.create(
                name=f'{city} Verified Clinic',
                clinic_type='virtual_clinic',
                description=f'A verified e-clinic in {city}',
                phone=f'+9198765433{i+1:02d}',
                email=f'{city.lower()}clinic@example.com',
                website=f'https://{city.lower()}clinic.com',
                street=f'Plot {200+i}, Main Road',
                city=city,
                state='Odisha',
                pincode=f'76{i+1:03d}',
                country='India',
                latitude=20.0 + i,
                longitude=85.0 + i,
                operating_hours={'monday': {'start': '09:00', 'end': '18:00'}},
                specialties=['General Medicine', 'Pediatrics'],
                services=['Consultation', 'Telemedicine'],
                facilities=['Video Call', 'Pharmacy'],
                registration_number=f'VERREG20250{i+1:02d}',
                license_number=f'VERLIC20250{i+1:02d}',
                accreditation='NABH',
                is_active=True,
                is_verified=True,
                accepts_online_consultations=True,
                admin=admin,
            )
            self.stdout.write(self.style.SUCCESS(f'Created verified e-clinic {clinic.name} assigned to admin {admin.name} ({admin.phone})')) 