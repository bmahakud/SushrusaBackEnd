from django.core.management.base import BaseCommand
from authentication.models import User

class Command(BaseCommand):
    help = 'Create multiple verified admin users with real Odia names and profiles.'

    def handle(self, *args, **options):
        admin_data = [
            {'name': 'Sasmita Pradhan', 'phone': '+919000000101'},
            {'name': 'Manaswini Das', 'phone': '+919000000102'},
            {'name': 'Sourav Mohanty', 'phone': '+919000000103'},
            {'name': 'Rashmi Ranjan Sahu', 'phone': '+919000000104'},
            {'name': 'Pragyan Parija', 'phone': '+919000000105'},
            {'name': 'Satyabrata Nayak', 'phone': '+919000000106'},
            {'name': 'Ipsita Swain', 'phone': '+919000000107'},
            {'name': 'Debasis Behera', 'phone': '+919000000108'},
            {'name': 'Lopamudra Patra', 'phone': '+919000000109'},
            {'name': 'Sibani Panda', 'phone': '+919000000110'},
        ]
        for data in admin_data:
            user, created = User.objects.get_or_create(
                phone=data['phone'],
                defaults={
                    'name': data['name'],
                    'role': 'admin',
                    'is_verified': True,
                }
            )
            if not created:
                user.name = data['name']
                user.role = 'admin'
                user.is_verified = True
                user.save(update_fields=['name', 'role', 'is_verified'])
            self.stdout.write(self.style.SUCCESS(f'Admin {data["name"]} ({data["phone"]}) created/verified.')) 