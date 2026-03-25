import random
from django.core.management.base import BaseCommand
from authentication.models import User
from doctors.models import DoctorProfile
from django.utils.crypto import get_random_string

class Command(BaseCommand):
    help = 'Create 10 verified doctor accounts and profiles with realistic Odia details.'

    def handle(self, *args, **options):
        odia_names = [
            'Dr. Subrat Kumar', 'Dr. Sasmita Das', 'Dr. Prakash Mohanty', 'Dr. Ananya Mishra',
            'Dr. Rakesh Sahu', 'Dr. Lopa Mudra', 'Dr. Manoj Nayak', 'Dr. Priya Rani',
            'Dr. Satyabrata Panda', 'Dr. Madhusmita Patra'
        ]
        phones = [
            '+919000000101', '+919000000102', '+919000000103', '+919000000104',
            '+919000000105', '+919000000106', '+919000000107', '+919000000108',
            '+919000000109', '+919000000110'
        ]
        specializations = [
            'cardiology', 'dermatology', 'endocrinology', 'gastroenterology', 'general_medicine',
            'gynecology', 'neurology', 'oncology', 'orthopedics', 'pediatrics'
        ]
        qualifications = [
            'MBBS, MD', 'MBBS, MS', 'MBBS, DM', 'MBBS, DNB', 'MBBS, MCh',
            'MBBS, MD', 'MBBS, MS', 'MBBS, DM', 'MBBS, DNB', 'MBBS, MCh'
        ]
        cities = [
            'Bhubaneswar', 'Cuttack', 'Puri', 'Sambalpur', 'Rourkela',
            'Berhampur', 'Balasore', 'Baripada', 'Jharsuguda', 'Angul'
        ]
        for i in range(10):
            name = odia_names[i]
            phone = phones[i]
            specialization = specializations[i]
            qualification = qualifications[i]
            city = cities[i]
            license_number = f'ODDOC{i+1:03d}'
            user, created = User.objects.get_or_create(
                phone=phone,
                defaults={
                    'name': name,
                    'role': 'doctor',
                    'is_verified': True,
                    'is_active': True,
                    'city': city,
                    'state': 'Odisha',
                    'country': 'India',
                    'password': get_random_string(10),
                }
            )
            if not created and user.role != 'doctor':
                user.role = 'doctor'
                user.is_verified = True
                user.is_active = True
                user.save()
            profile, prof_created = DoctorProfile.objects.get_or_create(
                user=user,
                defaults={
                    'license_number': license_number,
                    'qualification': qualification,
                    'specialization': specialization,
                    'sub_specialization': '',
                    'experience_years': random.randint(3, 20),
                    'consultation_fee': random.randint(300, 800),
                    'consultation_duration': 5,
                    'clinic_name': f'{city} Clinic',
                    'clinic_address': f'{city}, Odisha',
                    'is_online_consultation_available': True,
                    'online_consultation_fee': random.randint(300, 800),
                    'languages_spoken': ['Odia', 'Hindi', 'English'],
                    'bio': f'Experienced {specialization.replace("_", " ")} specialist from {city}.',
                    'achievements': '',
                    'is_verified': True,
                    'is_active': True,
                    'is_accepting_patients': True,
                }
            )
            if not prof_created:
                profile.is_verified = True
                profile.is_active = True
                profile.save()
            self.stdout.write(self.style.SUCCESS(f'Created/verified doctor: {name} ({phone})')) 