from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
import random

from authentication.models import User
from consultations.models import Consultation
from payments.models import Payment
from eclinic.models import Clinic
from doctors.models import DoctorProfile


class Command(BaseCommand):
    help = 'Generate test data for analytics endpoints'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clinics',
            type=int,
            default=3,
            help='Number of clinics to create'
        )
        parser.add_argument(
            '--doctors',
            type=int,
            default=5,
            help='Number of doctors to create'
        )
        parser.add_argument(
            '--patients',
            type=int,
            default=20,
            help='Number of patients to create'
        )
        parser.add_argument(
            '--consultations',
            type=int,
            default=50,
            help='Number of consultations to create'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Generating test analytics data...'))
        
        with transaction.atomic():
            # Create clinics
            clinics = self.create_clinics(options['clinics'])
            
            # Create doctors
            doctors = self.create_doctors(options['doctors'], clinics)
            
            # Create patients
            patients = self.create_patients(options['patients'])
            
            # Create consultations and payments
            self.create_consultations_and_payments(
                options['consultations'], 
                doctors, 
                patients, 
                clinics
            )
        
        self.stdout.write(self.style.SUCCESS('Test analytics data generated successfully!'))

    def create_clinics(self, count):
        """Create test clinics"""
        clinics = []
        # Create admin users for clinics
        admins = []
        for i in range(count):
            admin = User.objects.create(
                phone=f'+91{random.randint(7000000000, 9999999999)}',
                name=f'Test Admin {i+1}',
                email=f'admin{i+1}@test.com',
                role='admin',
                is_verified=True,
                is_active=True
            )
            admins.append(admin)
            self.stdout.write(f'Created admin: {admin.name}')
        
        for i in range(count):
            clinic = Clinic.objects.create(
                name=f'Test Clinic {i+1}',
                clinic_type='general',
                description=f'Test clinic description {i+1}',
                phone=f'+91{random.randint(7000000000, 9999999999)}',
                email=f'clinic{i+1}@test.com',
                street=f'Test Street {i+1}',
                city=f'Test City {i+1}',
                state=f'Test State {i+1}',
                pincode=f'{random.randint(100000, 999999)}',
                country='India',
                registration_number=f'REG{i+1:03d}',
                license_number=f'LIC{i+1:03d}',
                is_active=True,
                is_verified=True,
                accepts_online_consultations=True,
                consultation_duration=5,
                admin=admins[i]
            )
            clinics.append(clinic)
            self.stdout.write(f'Created clinic: {clinic.name}')
        
        return clinics

    def create_doctors(self, count, clinics):
        """Create test doctors"""
        doctors = []
        specializations = ['cardiology', 'dermatology', 'general_medicine', 'pediatrics', 'orthopedics']
        
        for i in range(count):
            # Create user
            user = User.objects.create(
                phone=f'+91{random.randint(7000000000, 9999999999)}',
                name=f'Dr. Test Doctor {i+1}',
                email=f'doctor{i+1}@test.com',
                role='doctor',
                is_verified=True,
                is_active=True
            )
            
            # Create doctor profile
            doctor_profile = DoctorProfile.objects.create(
                user=user,
                license_number=f'DOC{i+1:03d}',
                qualification='MBBS, MD',
                specialization=random.choice(specializations),
                experience_years=random.randint(5, 20),
                consultation_fee=random.randint(500, 2000),
                consultation_duration=5,
                is_verified=True,
                is_active=True,
                is_accepting_patients=True,
                rating=random.uniform(3.5, 5.0),
                total_reviews=random.randint(10, 100)
            )
            
            doctors.append(user)
            self.stdout.write(f'Created doctor: {user.name}')
        
        return doctors

    def create_patients(self, count):
        """Create test patients"""
        patients = []
        for i in range(count):
            user = User.objects.create(
                phone=f'+91{random.randint(7000000000, 9999999999)}',
                name=f'Test Patient {i+1}',
                email=f'patient{i+1}@test.com',
                role='patient',
                is_verified=True,
                is_active=True
            )
            patients.append(user)
            self.stdout.write(f'Created patient: {user.name}')
        
        return patients

    def create_consultations_and_payments(self, count, doctors, patients, clinics):
        """Create test consultations and payments"""
        statuses = ['scheduled', 'completed', 'cancelled']
        payment_methods = ['online', 'card', 'upi']
        
        for i in range(count):
            doctor = random.choice(doctors)
            patient = random.choice(patients)
            clinic = random.choice(clinics)
            status = random.choice(statuses)
            
            # Create consultation
            consultation = Consultation.objects.create(
                patient=patient,
                doctor=doctor,
                consultation_type='video_call',
                scheduled_date=timezone.now().date() - timedelta(days=random.randint(0, 30)),
                scheduled_time=f'{random.randint(9, 17)}:00:00',
                duration=30,
                status=status,
                payment_status='paid' if status == 'completed' else 'pending',
                consultation_fee=random.randint(500, 2000),
                is_paid=status == 'completed',
                chief_complaint=f'Test complaint {i+1}',
                clinic=clinic
            )
            
            # Create payment if consultation is completed
            if status == 'completed':
                try:
                    Payment.objects.create(
                        consultation=consultation,
                        patient=patient,
                        doctor=doctor,
                        amount=consultation.consultation_fee,
                        payment_method=random.choice(payment_methods),
                        status='completed',
                        completed_at=consultation.scheduled_date,
                        description=f'Payment for consultation {consultation.id}'
                    )
                except Exception as e:
                    self.stdout.write(f'Warning: Could not create payment for consultation {consultation.id}: {e}')
            
            self.stdout.write(f'Created consultation: {consultation.id} ({status})') 