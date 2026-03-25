from django.test import TestCase
from .models import Clinic
from django.contrib.auth import get_user_model

User = get_user_model()

class ClinicModelTest(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(phone='+911234567890', name='Admin User', role='admin')
        self.clinic_data = {
            'name': 'Test E-Clinic',
            'clinic_type': 'virtual_clinic',
            'description': 'A test e-clinic',
            'phone': '+911234567891',
            'email': 'clinic@example.com',
            'website': 'https://clinic.example.com',
            'street': '123 Main St',
            'city': 'Metropolis',
            'state': 'State',
            'pincode': '123456',
            'country': 'India',
            'latitude': 19.0760,
            'longitude': 72.8777,
            'operating_hours': {'monday': {'start': '09:00', 'end': '18:00'}},
            'specialties': ['General Medicine'],
            'services': ['Consultation'],
            'facilities': ['Video Call'],
            'registration_number': 'REG123',
            'license_number': 'LIC456',
            'accreditation': 'NABH',
            'is_active': True,
            'accepts_online_consultations': True,
            'admin': self.admin
        }

    def test_create_clinic(self):
        clinic = Clinic.objects.create(**self.clinic_data)
        self.assertEqual(clinic.name, 'Test E-Clinic')
        self.assertEqual(clinic.admin, self.admin)
        self.assertTrue(clinic.is_active)
        self.assertEqual(clinic.clinic_type, 'virtual_clinic')
        self.assertEqual(clinic.specialties, ['General Medicine'])
        self.assertEqual(clinic.registration_number, 'REG123')
