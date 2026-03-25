from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Investigate duplicate phone numbers in the database'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('=' * 60)
        )
        self.stdout.write(
            self.style.SUCCESS('INVESTIGATING DUPLICATE PHONE NUMBERS')
        )
        self.stdout.write(
            self.style.SUCCESS('=' * 60)
        )
        
        # Get all users with phone numbers
        all_users = User.objects.all().order_by('phone', 'id')
        
        self.stdout.write(f'\nTotal users in database: {all_users.count()}')
        
        # Group by phone number
        phone_groups = {}
        for user in all_users:
            if user.phone in phone_groups:
                phone_groups[user.phone].append(user)
            else:
                phone_groups[user.phone] = [user]
        
        # Find duplicates
        duplicates = {phone: users for phone, users in phone_groups.items() if len(users) > 1}
        
        self.stdout.write(f'\nPhone numbers with duplicates: {len(duplicates)}')
        
        if duplicates:
            for phone, users in duplicates.items():
                self.stdout.write(f'\nPhone: {phone} ({len(users)} users)')
                for user in users:
                    self.stdout.write(f'  - {user.id}: {user.name} (role: {user.role})')
        
        # Check ADM doctors specifically
        self.stdout.write(f'\n' + '=' * 60)
        self.stdout.write('ADM DOCTORS ANALYSIS')
        self.stdout.write('=' * 60)
        
        adm_doctors = User.objects.filter(id__startswith='ADM', role='doctor')
        
        for doctor in adm_doctors:
            self.stdout.write(f'\nADM Doctor: {doctor.id} - {doctor.name} - {doctor.phone}')
            
            # Check all users with this phone number
            users_with_same_phone = User.objects.filter(phone=doctor.phone)
            self.stdout.write(f'  Users with phone {doctor.phone}: {users_with_same_phone.count()}')
            
            for user in users_with_same_phone:
                self.stdout.write(f'    - {user.id}: {user.name} (role: {user.role})')
                
                # Check if there's a doctor profile
                try:
                    from doctors.models import DoctorProfile
                    profile = DoctorProfile.objects.get(user=user)
                    self.stdout.write(f'      → Has doctor profile: {profile.specialization}')
                except:
                    self.stdout.write(f'      → No doctor profile')
        
        # Check DOC doctors
        self.stdout.write(f'\n' + '=' * 60)
        self.stdout.write('DOC DOCTORS ANALYSIS')
        self.stdout.write('=' * 60)
        
        doc_doctors = User.objects.filter(id__startswith='DOC', role='doctor')
        
        for doctor in doc_doctors:
            self.stdout.write(f'\nDOC Doctor: {doctor.id} - {doctor.name} - {doctor.phone}')
            
            # Check all users with this phone number
            users_with_same_phone = User.objects.filter(phone=doctor.phone)
            self.stdout.write(f'  Users with phone {doctor.phone}: {users_with_same_phone.count()}')
            
            for user in users_with_same_phone:
                self.stdout.write(f'    - {user.id}: {user.name} (role: {user.role})')
