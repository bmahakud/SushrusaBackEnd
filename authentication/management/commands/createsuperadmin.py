from django.core.management.base import BaseCommand
from authentication.models import User


class Command(BaseCommand):
    help = 'Create a superadmin user'

    def add_arguments(self, parser):
        parser.add_argument('phone', type=str, help='Phone number for the superadmin')
        parser.add_argument('name', type=str, help='Name for the superadmin')
        parser.add_argument('--email', type=str, default='', help='Email for the superadmin')
        parser.add_argument('--password', type=str, default='admin123', help='Password for the superadmin')

    def handle(self, *args, **options):
        phone = options['phone']
        name = options['name']
        email = options['email']
        password = options['password']

        # Check if user already exists
        if User.objects.filter(phone=phone).exists():
            user = User.objects.get(phone=phone)
            user.role = 'superadmin'
            user.is_staff = True
            user.is_superuser = True
            user.is_verified = True
            user.set_password(password)
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f'Updated existing user {phone} to superadmin role')
            )
        else:
            # Create new superadmin user
            user = User.objects.create_user(
                phone=phone,
                name=name,
                email=email,
                role='superadmin',
                is_staff=True,
                is_superuser=True,
                is_verified=True
            )
            user.set_password(password)
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created superadmin user: {phone}')
            )

        self.stdout.write(f'User ID: {user.id}')
        self.stdout.write(f'Phone: {user.phone}')
        self.stdout.write(f'Name: {user.name}')
        self.stdout.write(f'Role: {user.role}')
        self.stdout.write(f'Password: {password}') 