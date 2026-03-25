from django.core.management.base import BaseCommand
from authentication.models import User
from authentication.utils import format_phone_number

class Command(BaseCommand):
    help = 'Normalize all user phone numbers to +91XXXXXXXXXX format.'

    def handle(self, *args, **options):
        updated = 0
        for user in User.objects.all():
            normalized = format_phone_number(user.phone)
            if user.phone != normalized:
                self.stdout.write(f'Updating {user.phone} -> {normalized}')
                user.phone = normalized
                user.save(update_fields=['phone'])
                updated += 1
        self.stdout.write(self.style.SUCCESS(f'Normalized {updated} phone numbers.')) 