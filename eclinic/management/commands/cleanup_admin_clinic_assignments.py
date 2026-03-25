from django.core.management.base import BaseCommand
from authentication.models import User
from eclinic.models import Clinic
from django.db import transaction

class Command(BaseCommand):
    help = 'Ensure each verified admin is assigned to only one clinic. For each admin with multiple clinics, keep only the first and delete the rest.'

    def handle(self, *args, **options):
        admins = User.objects.filter(role='admin', is_verified=True)
        total_deleted = 0
        with transaction.atomic():
            for admin in admins:
                clinics = Clinic.objects.filter(admin=admin).order_by('created_at')
                if clinics.count() > 1:
                    to_delete = clinics.exclude(id=clinics.first().id)
                    count = to_delete.count()
                    to_delete.delete()
                    self.stdout.write(f'Deleted {count} extra clinics for admin {admin.name} ({admin.phone})')
                    total_deleted += count
        self.stdout.write(self.style.SUCCESS(f'Total extra clinics deleted: {total_deleted}')) 