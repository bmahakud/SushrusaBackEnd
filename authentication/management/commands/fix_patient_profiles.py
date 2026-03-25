
from django.core.management.base import BaseCommand
from authentication.models import User
from patients.models import PatientProfile
from django.utils import timezone

class Command(BaseCommand):
    help = 'Fix incomplete patient accounts by creating missing PatientProfiles'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--create-missing',
            action='store_true',
            help='Create PatientProfile for patients who do not have one',
        )
        parser.add_argument(
            '--deactivate-incomplete',
            action='store_true',
            help='Deactivate users without PatientProfile',
        )
        parser.add_argument(
            '--list-incomplete',
            action='store_true',
            help='List patients without PatientProfile',
        )
    
    def handle(self, *args, **options):
        if options['list_incomplete']:
            self.list_incomplete_patients()
        elif options['create_missing']:
            self.create_missing_profiles()
        elif options['deactivate_incomplete']:
            self.deactivate_incomplete_patients()
        else:
            self.stdout.write(self.style.WARNING('Please specify an action. Use --help for options.'))
    
    def list_incomplete_patients(self):
        """List patients without PatientProfile"""
        incomplete_patients = User.objects.filter(
            role='patient',
            patient_profile__isnull=True
        )
        
        self.stdout.write(f"Found {incomplete_patients.count()} patients without PatientProfile:")
        for patient in incomplete_patients:
            self.stdout.write(f"  - {patient.id}: {patient.name} ({patient.phone})")
    
    def create_missing_profiles(self):
        """Create PatientProfile for patients who don't have one"""
        incomplete_patients = User.objects.filter(
            role='patient',
            patient_profile__isnull=True
        )
        
        created_count = 0
        for patient in incomplete_patients:
            try:
                PatientProfile.objects.create(
                    user=patient,
                    is_active=True
                )
                created_count += 1
                self.stdout.write(f"Created PatientProfile for {patient.name} ({patient.phone})")
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Failed to create PatientProfile for {patient.name}: {str(e)}")
                )
        
        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {created_count} PatientProfiles")
        )
    
    def deactivate_incomplete_patients(self):
        """Deactivate users without PatientProfile"""
        incomplete_patients = User.objects.filter(
            role='patient',
            patient_profile__isnull=True
        )
        
        deactivated_count = incomplete_patients.update(is_active=False)
        
        self.stdout.write(
            self.style.SUCCESS(f"Deactivated {deactivated_count} incomplete patient accounts")
        )
