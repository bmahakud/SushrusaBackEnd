from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from doctors.models import DoctorProfile

User = get_user_model()


class Command(BaseCommand):
    help = 'Fix doctor IDs that have ADM prefix instead of DOC prefix (Version 2 - handles duplicates)'

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
            self.style.SUCCESS('SUSHURSA HEALTHCARE - DOCTOR ID PREFIX FIX V2')
        )
        self.stdout.write(
            self.style.SUCCESS('=' * 60)
        )
        
        # Find doctors with ADM prefix
        self.stdout.write('\n1. Finding doctors with ADM prefix...')
        adm_doctors = User.objects.filter(id__startswith='ADM', role='doctor')
        self.stdout.write(f'   Found {adm_doctors.count()} doctors with ADM prefix')
        
        if adm_doctors.count() == 0:
            self.stdout.write('   No doctors with ADM prefix found. Exiting...')
            return
        
        # Show current ADM doctors
        self.stdout.write('\n2. Current ADM doctors:')
        for doctor in adm_doctors:
            self.stdout.write(f'   - {doctor.id}: {doctor.name} ({doctor.phone})')
        
        # Check for duplicate phone numbers
        self.stdout.write('\n3. Checking for duplicate phone numbers...')
        duplicate_phones = []
        for doctor in adm_doctors:
            users_with_same_phone = User.objects.filter(phone=doctor.phone)
            if users_with_same_phone.count() > 1:
                duplicate_phones.append(doctor.phone)
                self.stdout.write(f'   ⚠️  Duplicate phone {doctor.phone}:')
                for user in users_with_same_phone:
                    self.stdout.write(f'      - {user.id}: {user.name} ({user.role})')
        
        if duplicate_phones:
            self.stdout.write(f'\n   Found {len(duplicate_phones)} duplicate phone numbers')
            self.stdout.write('   This suggests there are duplicate doctors in the database')
        
        # Get the last DOC number
        self.stdout.write('\n4. Finding next available DOC number...')
        last_doc_user = User.objects.filter(id__startswith='DOC').order_by('id').last()
        if last_doc_user:
            last_doc_number = int(last_doc_user.id[3:])
            next_doc_number = last_doc_number + 1
            self.stdout.write(f'   Last DOC number: {last_doc_number}')
            self.stdout.write(f'   Next DOC number: {next_doc_number}')
        else:
            next_doc_number = 1
            self.stdout.write(f'   No existing DOC users found. Starting from: {next_doc_number}')
        
        # Strategy: For duplicate phones, we'll keep the DOC version and delete the ADM version
        self.stdout.write('\n5. Strategy for duplicates:')
        self.stdout.write('   - If phone number exists in both ADM and DOC: Keep DOC, delete ADM')
        self.stdout.write('   - If phone number only exists in ADM: Rename ADM to DOC')
        
        # Show proposed changes
        self.stdout.write(f'\n6. Proposed changes:')
        changes_made = 0
        for i, doctor in enumerate(adm_doctors):
            # Check if there's already a DOC doctor with the same phone
            existing_doc_doctor = User.objects.filter(
                phone=doctor.phone, 
                id__startswith='DOC',
                role='doctor'
            ).first()
            
            if existing_doc_doctor:
                self.stdout.write(f'   - DELETE {doctor.id}: {doctor.name} (duplicate of {existing_doc_doctor.id})')
                changes_made += 1
            else:
                new_id = f"DOC{next_doc_number + changes_made:03d}"
                self.stdout.write(f'   - RENAME {doctor.id} → {new_id}: {doctor.name}')
                changes_made += 1
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('\n[DRY RUN] No changes were made. Use without --dry-run to apply changes.')
            )
            return
        
        # Confirm the fix
        response = input('\n   Do you want to proceed with the fix? (y/N): ')
        if response.lower() != 'y':
            self.stdout.write('   Operation cancelled by user.')
            return
        
        # Perform the fix
        self.stdout.write('\n7. Applying changes...')
        updated_count = 0
        deleted_count = 0
        errors = []
        
        for i, doctor in enumerate(adm_doctors):
            try:
                old_id = doctor.id
                
                # Check if there's already a DOC doctor with the same phone
                existing_doc_doctor = User.objects.filter(
                    phone=doctor.phone, 
                    id__startswith='DOC',
                    role='doctor'
                ).first()
                
                if existing_doc_doctor:
                    # Delete the ADM duplicate
                    self.stdout.write(f'   Deleting duplicate {old_id}: {doctor.name}')
                    
                    # Check if ADM doctor has a profile that needs to be merged
                    try:
                        adm_profile = DoctorProfile.objects.get(user=doctor)
                        self.stdout.write(f'   → ADM doctor has profile: {adm_profile.specialization}')
                        
                        # Check if DOC doctor already has a profile
                        try:
                            doc_profile = DoctorProfile.objects.get(user=existing_doc_doctor)
                            self.stdout.write(f'   → DOC doctor already has profile: {doc_profile.specialization}')
                            self.stdout.write(f'   → Keeping DOC profile, deleting ADM profile')
                            adm_profile.delete()
                        except DoctorProfile.DoesNotExist:
                            self.stdout.write(f'   → DOC doctor has no profile, transferring ADM profile')
                            adm_profile.user = existing_doc_doctor
                            adm_profile.save()
                    except DoctorProfile.DoesNotExist:
                        self.stdout.write(f'   → ADM doctor has no profile')
                    
                    # Delete the ADM user
                    doctor.delete()
                    deleted_count += 1
                    self.stdout.write(f'   ✓ Deleted duplicate: {old_id}')
                    
                else:
                    # Rename ADM to DOC
                    new_id = f"DOC{next_doc_number + updated_count:03d}"
                    self.stdout.write(f'   Renaming {old_id} → {new_id}: {doctor.name}')
                    
                    # Update the user ID directly using raw SQL to avoid constraints
                    from django.db import connection
                    with connection.cursor() as cursor:
                        # Update all foreign key references first
                        tables_to_update = [
                            'doctor_profiles',
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
                                    self.stdout.write(f'   → Updated {affected} records in {table}')
                            except Exception as e:
                                # Table might not exist or have user_id column
                                pass
                        
                        # Finally update the user ID
                        cursor.execute('UPDATE users SET id = %s WHERE id = %s', [new_id, old_id])
                    
                    updated_count += 1
                    self.stdout.write(f'   ✓ Renamed: {old_id} → {new_id}')
                    
            except Exception as e:
                errors.append(f"Error processing {doctor.id}: {str(e)}")
                self.stdout.write(
                    self.style.ERROR(f'   ✗ Failed to process {doctor.id}: {str(e)}')
                )
        
        # Show results
        self.stdout.write(f'\n8. Results:')
        self.stdout.write(f'   ✓ Successfully renamed: {updated_count} doctors')
        self.stdout.write(f'   ✓ Successfully deleted: {deleted_count} duplicates')
        if errors:
            self.stdout.write(f'   ✗ Errors: {len(errors)}')
            for error in errors:
                self.stdout.write(
                    self.style.ERROR(f'     - {error}')
                )
        
        # Verify the fix
        self.stdout.write(f'\n9. Verification:')
        remaining_adm_doctors = User.objects.filter(id__startswith='ADM', role='doctor').count()
        doc_doctors = User.objects.filter(id__startswith='DOC', role='doctor').count()
        
        self.stdout.write(f'   Doctors with ADM prefix: {remaining_adm_doctors}')
        self.stdout.write(f'   Doctors with DOC prefix: {doc_doctors}')
        
        if remaining_adm_doctors == 0:
            self.stdout.write(
                self.style.SUCCESS('\n' + '=' * 60)
            )
            self.stdout.write(
                self.style.SUCCESS('DOCTOR ID PREFIX FIX COMPLETED SUCCESSFULLY!')
            )
            self.stdout.write(
                self.style.SUCCESS('=' * 60)
            )
            self.stdout.write(f'\n✓ All doctors now have DOC prefix')
            self.stdout.write(f'✓ {updated_count} doctors renamed, {deleted_count} duplicates removed')
            self.stdout.write('✓ API endpoints should now work correctly')
        else:
            self.stdout.write(
                self.style.WARNING(f'\n⚠ Warning: {remaining_adm_doctors} doctors still have ADM prefix')
            )
            self.stdout.write('  Please check the errors above and try again')
