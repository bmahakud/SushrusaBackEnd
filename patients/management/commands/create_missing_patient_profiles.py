from django.core.management.base import BaseCommand
from authentication.models import User
from patients.models import PatientProfile

class Command(BaseCommand):
    help = 'Create PatientProfile for all users with role="patient" who do not have one.'

    def handle(self, *args, **options):
        created = 0
        for user in User.objects.filter(role='patient'):
            if not hasattr(user, 'patient_profile'):
                PatientProfile.objects.create(user=user)
                self.stdout.write(self.style.SUCCESS(f"Created PatientProfile for user {user.id} ({user.phone})"))
                created += 1
        self.stdout.write(self.style.SUCCESS(f"Done. Created {created} PatientProfiles.")) 