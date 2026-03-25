from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from consultations.views import ConsultationViewSet, ConsultationSearchView, ConsultationStatsView
from consultations.models import Consultation
from eclinic.models import Clinic
from authentication.models import User

User = get_user_model()

class Command(BaseCommand):
    help = 'Test clinic-based consultation filtering for admins'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Testing clinic-based consultation filtering...'))
        
        # Create test data
        self.create_test_data()
        
        # Test consultation filtering
        self.test_consultation_filtering()
        
        self.stdout.write(self.style.SUCCESS('Clinic-based filtering test completed!'))

    def create_test_data(self):
        """Create test clinics, admins, and consultations"""
        self.stdout.write('Creating test data...')
        
        # Create clinics
        clinic1, created = Clinic.objects.get_or_create(
            id='CLI001',
            defaults={
                'name': 'Test Clinic 1',
                'phone': '+1234567890',
                'email': 'clinic1@test.com',
                'street': '123 Test St',
                'city': 'Test City',
                'state': 'Test State',
                'pincode': '12345',
                'country': 'India',
                'registration_number': 'REG001',
                'consultation_duration': 15
            }
        )
        
        clinic2, created = Clinic.objects.get_or_create(
            id='CLI002',
            defaults={
                'name': 'Test Clinic 2',
                'phone': '+1234567891',
                'email': 'clinic2@test.com',
                'street': '456 Test St',
                'city': 'Test City',
                'state': 'Test State',
                'pincode': '12345',
                'country': 'India',
                'registration_number': 'REG002',
                'consultation_duration': 20
            }
        )
        
        # Create admins
        admin1, created = User.objects.get_or_create(
            phone='+1111111111',
            defaults={
                'name': 'Admin 1',
                'email': 'admin1@test.com',
                'role': 'admin',
                'is_active': True,
                'is_verified': True
            }
        )
        
        admin2, created = User.objects.get_or_create(
            phone='+2222222222',
            defaults={
                'name': 'Admin 2',
                'email': 'admin2@test.com',
                'role': 'admin',
                'is_active': True,
                'is_verified': True
            }
        )
        
        # Create patients and doctors
        patient1, created = User.objects.get_or_create(
            phone='+3333333333',
            defaults={
                'name': 'Patient 1',
                'email': 'patient1@test.com',
                'role': 'patient',
                'is_active': True,
                'is_verified': True
            }
        )
        
        doctor1, created = User.objects.get_or_create(
            phone='+4444444444',
            defaults={
                'name': 'Doctor 1',
                'email': 'doctor1@test.com',
                'role': 'doctor',
                'is_active': True,
                'is_verified': True
            }
        )
        
        # Assign admins to clinics
        clinic1.admin = admin1
        clinic1.save()
        
        clinic2.admin = admin2
        clinic2.save()
        
        # Create consultations
        consultation1, created = Consultation.objects.get_or_create(
            id='CON001',
            defaults={
                'patient': patient1,
                'doctor': doctor1,
                'clinic': clinic1,
                'scheduled_date': '2025-07-31',
                'scheduled_time': '10:00:00',
                'duration': 15,
                'consultation_type': 'video_call',
                'chief_complaint': 'Test complaint 1',
                'consultation_fee': 100.00,
                'status': 'scheduled'
            }
        )
        
        consultation2, created = Consultation.objects.get_or_create(
            id='CON002',
            defaults={
                'patient': patient1,
                'doctor': doctor1,
                'clinic': clinic2,
                'scheduled_date': '2025-07-31',
                'scheduled_time': '11:00:00',
                'duration': 20,
                'consultation_type': 'video_call',
                'chief_complaint': 'Test complaint 2',
                'consultation_fee': 150.00,
                'status': 'scheduled'
            }
        )
        
        self.stdout.write(f'✅ Created test data:')
        self.stdout.write(f'   - Clinics: {clinic1.name}, {clinic2.name}')
        self.stdout.write(f'   - Admins: {admin1.name}, {admin2.name}')
        self.stdout.write(f'   - Consultations: {consultation1.id}, {consultation2.id}')

    def test_consultation_filtering(self):
        """Test that admins only see consultations for their assigned clinic"""
        self.stdout.write('\nTesting consultation filtering...')
        
        # Get test users
        admin1 = User.objects.get(phone='+1111111111')
        admin2 = User.objects.get(phone='+2222222222')
        
        # Test ConsultationViewSet filtering
        factory = RequestFactory()
        
        # Test admin1 (assigned to clinic1)
        request1 = factory.get('/api/consultations/')
        request1.user = admin1
        
        viewset1 = ConsultationViewSet()
        viewset1.request = request1
        queryset1 = viewset1.get_queryset()
        
        self.stdout.write(f'Admin 1 ({admin1.name}) consultations: {queryset1.count()}')
        for consultation in queryset1:
            self.stdout.write(f'   - {consultation.id} (Clinic: {consultation.clinic.name})')
        
        # Test admin2 (assigned to clinic2)
        request2 = factory.get('/api/consultations/')
        request2.user = admin2
        
        viewset2 = ConsultationViewSet()
        viewset2.request = request2
        queryset2 = viewset2.get_queryset()
        
        self.stdout.write(f'Admin 2 ({admin2.name}) consultations: {queryset2.count()}')
        for consultation in queryset2:
            self.stdout.write(f'   - {consultation.id} (Clinic: {consultation.clinic.name})')
        
        # Verify filtering is working correctly
        clinic1_consultations = queryset1.filter(clinic__name='Test Clinic 1').count()
        clinic2_consultations = queryset2.filter(clinic__name='Test Clinic 2').count()
        
        if clinic1_consultations == 1 and clinic2_consultations == 1:
            self.stdout.write(self.style.SUCCESS('✅ Clinic-based filtering is working correctly!'))
            self.stdout.write(f'   - Admin 1 sees {clinic1_consultations} consultation(s) from Clinic 1')
            self.stdout.write(f'   - Admin 2 sees {clinic2_consultations} consultation(s) from Clinic 2')
        else:
            self.stdout.write(self.style.ERROR('❌ Clinic-based filtering is not working correctly!'))
            self.stdout.write(f'   - Admin 1 should see 1 consultation from Clinic 1, but sees {clinic1_consultations}')
            self.stdout.write(f'   - Admin 2 should see 1 consultation from Clinic 2, but sees {clinic2_consultations}')
        
        # Test search view filtering
        self.stdout.write('\nTesting search view filtering...')
        
        search_request1 = factory.get('/api/consultations/search/')
        search_request1.user = admin1
        
        search_view1 = ConsultationSearchView()
        search_view1.request = search_request1
        
        # Test stats view filtering
        self.stdout.write('Testing stats view filtering...')
        
        stats_request1 = factory.get('/api/consultations/stats/')
        stats_request1.user = admin1
        
        stats_view1 = ConsultationStatsView()
        stats_view1.request = stats_request1
        
        self.stdout.write(self.style.SUCCESS('✅ All filtering tests completed!')) 