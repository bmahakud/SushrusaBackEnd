from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Delete ADM doctors that are causing phone number conflicts'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without making actual changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        self.stdout.write(
            self.style.SUCCESS('=' * 60)
        )
        self.stdout.write(
            self.style.SUCCESS('DELETE ADM DOCTORS (PHONE CONFLICT RESOLUTION)')
        )
        self.stdout.write(
            self.style.SUCCESS('=' * 60)
        )
        
        # Find ADM doctors
        adm_doctors = User.objects.filter(id__startswith='ADM', role='doctor')
        self.stdout.write(f'\nFound {adm_doctors.count()} ADM doctors to delete')
        
        if adm_doctors.count() == 0:
            self.stdout.write('No ADM doctors found. Exiting...')
            return
        
        # Show ADM doctors
        self.stdout.write('\nADM doctors to be deleted:')
        for doctor in adm_doctors:
            self.stdout.write(f'  - {doctor.id}: {doctor.name} ({doctor.phone})')
            
            # Check if there's a doctor profile
            try:
                from doctors.models import DoctorProfile
                profile = DoctorProfile.objects.get(user=doctor)
                self.stdout.write(f'    → Has doctor profile: {profile.specialization}')
            except:
                self.stdout.write(f'    → No doctor profile')
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('\n[DRY RUN] No changes were made. Use without --dry-run to apply changes.')
            )
            return
        
        # Confirm deletion
        response = input('\nAre you sure you want to delete all ADM doctors? (y/N): ')
        if response.lower() != 'y':
            self.stdout.write('Operation cancelled by user.')
            return
        
        # Delete ADM doctors
        self.stdout.write('\nDeleting ADM doctors...')
        deleted_count = 0
        errors = []
        
        for doctor in adm_doctors:
            try:
                doctor_id = doctor.id
                doctor_name = doctor.name
                
                # Check if there's a doctor profile to delete
                try:
                    from doctors.models import DoctorProfile
                    profile = DoctorProfile.objects.get(user=doctor)
                    profile.delete()
                    self.stdout.write(f'  → Deleted doctor profile for {doctor_id}')
                except:
                    pass
                
                # Delete the user
                doctor.delete()
                deleted_count += 1
                self.stdout.write(f'  ✓ Deleted: {doctor_id} - {doctor_name}')
                
            except Exception as e:
                errors.append(f"Error deleting {doctor.id}: {str(e)}")
                self.stdout.write(
                    self.style.ERROR(f'  ✗ Failed to delete {doctor.id}: {str(e)}')
                )
        
        # Show results
        self.stdout.write(f'\nResults:')
        self.stdout.write(f'  ✓ Successfully deleted: {deleted_count} ADM doctors')
        if errors:
            self.stdout.write(f'  ✗ Errors: {len(errors)}')
            for error in errors:
                self.stdout.write(
                    self.style.ERROR(f'    - {error}')
                )
        
        # Verify
        self.stdout.write(f'\nVerification:')
        remaining_adm_doctors = User.objects.filter(id__startswith='ADM', role='doctor').count()
        doc_doctors = User.objects.filter(id__startswith='DOC', role='doctor').count()
        
        self.stdout.write(f'  ADM doctors remaining: {remaining_adm_doctors}')
        self.stdout.write(f'  DOC doctors: {doc_doctors}')
        
        if remaining_adm_doctors == 0:
            self.stdout.write(
                self.style.SUCCESS('\n' + '=' * 60)
            )
            self.stdout.write(
                self.style.SUCCESS('ADM DOCTORS DELETION COMPLETED SUCCESSFULLY!')
            )
            self.stdout.write(
                self.style.SUCCESS('=' * 60)
            )
            self.stdout.write(f'\n✓ All ADM doctors deleted')
            self.stdout.write('✓ Phone number conflicts resolved')
            self.stdout.write('✓ API endpoints should now work correctly')
        else:
            self.stdout.write(
                self.style.WARNING(f'\n⚠ Warning: {remaining_adm_doctors} ADM doctors still exist')
            )
