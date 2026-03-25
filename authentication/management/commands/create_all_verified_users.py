from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Create superadmin, batch of verified admins, and all missing doctor/patient profiles in one step.'

    def add_arguments(self, parser):
        parser.add_argument('--superadmin-phone', type=str, default='+919000000001', help='Phone number for the superadmin')
        parser.add_argument('--superadmin-name', type=str, default='Super Admin', help='Name for the superadmin')
        parser.add_argument('--superadmin-email', type=str, default='superadmin@sushrusa.com', help='Email for the superadmin')
        parser.add_argument('--superadmin-password', type=str, default='superpass123', help='Password for the superadmin')

    def handle(self, *args, **options):
        # 1. Create superadmin
        self.stdout.write(self.style.NOTICE('Creating superadmin...'))
        call_command(
            'createsuperadmin',
            options['superadmin_phone'],
            options['superadmin_name'],
            email=options['superadmin_email'],
            password=options['superadmin_password']
        )
        # 2. Create batch of verified admins
        self.stdout.write(self.style.NOTICE('Creating batch of verified admins...'))
        call_command('create_verified_admins')
        # 3. Create missing doctor and patient profiles
        self.stdout.write(self.style.NOTICE('Creating missing doctor and patient profiles...'))
        call_command('create_missing_profiles')
        self.stdout.write(self.style.SUCCESS('All users and profiles created/verified successfully!')) 