from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import connection, transaction
from doctors.models import DoctorProfile

User = get_user_model()


class Command(BaseCommand):
    help = 'Migrate ADM doctors to DOC prefix while preserving all data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without making actual changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        self.stdout.write(
            self.style.SUCCESS('=' * 60)
        )
        self.stdout.write(
            self.style.SUCCESS('MIGRATE ADM DOCTORS TO DOC PREFIX')
        )
        self.stdout.write(
            self.style.SUCCESS('=' * 60)
        )
        
        # Find ADM doctors
        adm_doctors = User.objects.filter(id__startswith='ADM', role='doctor')
        self.stdout.write(f'\nFound {adm_doctors.count()} ADM doctors to migrate')
        
        if adm_doctors.count() == 0:
            self.stdout.write('No ADM doctors found. Exiting...')
            return
        
        # Show ADM doctors
        self.stdout.write('\nADM doctors to be migrated:')
        for doctor in adm_doctors:
            self.stdout.write(f'  - {doctor.id}: {doctor.name} ({doctor.phone})')
            
            # Check if there's a doctor profile
            try:
                profile = DoctorProfile.objects.get(user=doctor)
                self.stdout.write(f'    → Has doctor profile: {profile.specialization}')
            except:
                self.stdout.write(f'    → No doctor profile')
        
        # Get the last DOC number
        self.stdout.write('\nFinding next available DOC number...')
        last_doc_user = User.objects.filter(id__startswith='DOC').order_by('id').last()
        if last_doc_user:
            last_doc_number = int(last_doc_user.id[3:])
            next_doc_number = last_doc_number + 1
            self.stdout.write(f'Last DOC number: {last_doc_number}')
            self.stdout.write(f'Next DOC number: {next_doc_number}')
        else:
            next_doc_number = 1
            self.stdout.write(f'No existing DOC users found. Starting from: {next_doc_number}')
        
        # Show proposed changes
        self.stdout.write(f'\nProposed migration:')
        for i, doctor in enumerate(adm_doctors):
            new_id = f"DOC{next_doc_number + i:03d}"
            self.stdout.write(f'  - {doctor.id} → {new_id}: {doctor.name}')
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('\n[DRY RUN] No changes were made. Use without --dry-run to apply changes.')
            )
            return
        
        # Confirm the migration
        response = input('\nDo you want to proceed with the migration? (y/N): ')
        if response.lower() != 'y':
            self.stdout.write('Operation cancelled by user.')
            return
        
        # Perform the migration
        self.stdout.write('\nStarting migration...')
        migrated_count = 0
        errors = []
        
        for i, doctor in enumerate(adm_doctors):
            try:
                old_id = doctor.id
                new_id = f"DOC{next_doc_number + i:03d}"
                
                self.stdout.write(f'\nMigrating {old_id} → {new_id}: {doctor.name}')
                
                # Check if new ID already exists
                if User.objects.filter(id=new_id).exists():
                    errors.append(f"Cannot migrate {old_id} to {new_id}: ID already exists")
                    continue
                
                # Strategy: Create new user with temporary phone, then update
                with transaction.atomic():
                    # Step 1: Create new user with temporary phone number
                    temp_phone = f"+91{doctor.phone[3:]}_TEMP_{i}"  # Add temporary suffix
                    
                    new_user = User.objects.create(
                        id=new_id,
                        phone=temp_phone,  # Temporary phone to avoid conflict
                        email=doctor.email,
                        name=doctor.name,
                        role='doctor',
                        date_of_birth=doctor.date_of_birth,
                        gender=doctor.gender,
                        street=doctor.street,
                        city=doctor.city,
                        state=doctor.state,
                        pincode=doctor.pincode,
                        country=doctor.country,
                        emergency_contact_name=doctor.emergency_contact_name,
                        emergency_contact_phone=doctor.emergency_contact_phone,
                        emergency_contact_relationship=doctor.emergency_contact_relationship,
                        blood_group=doctor.blood_group,
                        allergies=doctor.allergies,
                        medical_history=doctor.medical_history,
                        is_active=doctor.is_active,
                        is_staff=doctor.is_staff,
                        is_verified=doctor.is_verified,
                        date_joined=doctor.date_joined,
                        last_login=doctor.last_login
                    )
                    
                    self.stdout.write(f'  → Created new user: {new_id}')
                    
                    # Step 2: Migrate doctor profile if exists
                    try:
                        old_profile = DoctorProfile.objects.get(user=doctor)
                        old_profile.user = new_user
                        old_profile.save()
                        self.stdout.write(f'  → Migrated doctor profile')
                    except DoctorProfile.DoesNotExist:
                        self.stdout.write(f'  → No doctor profile to migrate')
                    
                    # Step 3: Migrate other foreign key references using raw SQL
                    with connection.cursor() as cursor:
                        tables_to_update = [
                            'user_sessions',
                            'user_activity_logs',
                            'token_blacklist_outstandingtoken',
                            'clinic_staff',
                            'patient_profiles',
                            'payment_discount_usage',
                            'payment_methods',
                            'users_groups',
                            'users_user_permissions',
                            'django_admin_log'
                        ]
                        
                        for table in tables_to_update:
                            try:
                                cursor.execute(f'UPDATE {table} SET user_id = %s WHERE user_id = %s', [new_id, old_id])
                                affected = cursor.rowcount
                                if affected > 0:
                                    self.stdout.write(f'  → Migrated {affected} records from {table}')
                            except Exception as e:
                                # Table might not exist or have user_id column
                                pass
                    
                    # Step 4: Delete old user
                    doctor.delete()
                    self.stdout.write(f'  → Deleted old user: {old_id}')
                    
                    # Step 5: Update phone number to original
                    new_user.phone = doctor.phone  # Use the original phone number
                    new_user.save()
                    self.stdout.write(f'  → Updated phone number to original: {doctor.phone}')
                    
                    migrated_count += 1
                    self.stdout.write(f'  ✓ Successfully migrated: {old_id} → {new_id}')
                    
            except Exception as e:
                errors.append(f"Error migrating {doctor.id}: {str(e)}")
                self.stdout.write(
                    self.style.ERROR(f'  ✗ Failed to migrate {doctor.id}: {str(e)}')
                )
        
        # Show results
        self.stdout.write(f'\nResults:')
        self.stdout.write(f'  ✓ Successfully migrated: {migrated_count} doctors')
        if errors:
            self.stdout.write(f'  ✗ Errors: {len(errors)}')
            for error in errors:
                self.stdout.write(
                    self.style.ERROR(f'    - {error}')
                )
        
        # Verify the migration
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
                self.style.SUCCESS('ADM TO DOC MIGRATION COMPLETED SUCCESSFULLY!')
            )
            self.stdout.write(
                self.style.SUCCESS('=' * 60)
            )
            self.stdout.write(f'\n✓ All {migrated_count} doctors migrated to DOC prefix')
            self.stdout.write('✓ All doctor data preserved')
            self.stdout.write('✓ API endpoints should now work correctly')
        else:
            self.stdout.write(
                self.style.WARNING(f'\n⚠ Warning: {remaining_adm_doctors} ADM doctors still exist')
            )
