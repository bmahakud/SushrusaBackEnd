from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from datetime import datetime, timedelta
from consultations.models import Consultation
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Automatically mark overdue consultations as completed'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without actually updating',
        )
        parser.add_argument(
            '--hours-overdue',
            type=int,
            default=1,
            help='Number of hours after scheduled time to consider consultation overdue (default: 1)',
        )
        parser.add_argument(
            '--status',
            type=str,
            choices=['scheduled', 'in_progress', 'both'],
            default='both',
            help='Which status to check for overdue consultations (default: both)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        hours_overdue = options['hours_overdue']
        status_filter = options['status']
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Starting auto-completion of overdue consultations...\n'
                f'Dry run: {dry_run}\n'
                f'Hours overdue threshold: {hours_overdue}\n'
                f'Status filter: {status_filter}'
            )
        )
        
        # Calculate the cutoff time
        cutoff_time = timezone.now() - timedelta(hours=hours_overdue)
        
        # Build the query
        status_conditions = []
        if status_filter in ['scheduled', 'both']:
            status_conditions.append('scheduled')
        if status_filter in ['in_progress', 'both']:
            status_conditions.append('in_progress')
        
        if not status_conditions:
            self.stdout.write(
                self.style.ERROR('No valid status conditions specified')
            )
            return
        
        # Find overdue consultations
        overdue_consultations = Consultation.objects.filter(
            status__in=status_conditions
        ).select_related('patient', 'doctor')
        
        # Filter by scheduled datetime
        overdue_list = []
        for consultation in overdue_consultations:
            # Create scheduled datetime
            scheduled_datetime = datetime.combine(
                consultation.scheduled_date,
                consultation.scheduled_time
            )
            
            # Convert to timezone-aware datetime if needed
            if timezone.is_naive(scheduled_datetime):
                scheduled_datetime = timezone.make_aware(scheduled_datetime)
            
            # Check if consultation is overdue
            if scheduled_datetime < cutoff_time:
                overdue_list.append({
                    'consultation': consultation,
                    'scheduled_datetime': scheduled_datetime,
                    'hours_overdue': (timezone.now() - scheduled_datetime).total_seconds() / 3600
                })
        
        if not overdue_list:
            self.stdout.write(
                self.style.SUCCESS('No overdue consultations found!')
            )
            return
        
        # Display what will be updated
        self.stdout.write(
            self.style.WARNING(
                f'\nFound {len(overdue_list)} overdue consultation(s):'
            )
        )
        
        for item in overdue_list:
            consultation = item['consultation']
            hours_overdue = item['hours_overdue']
            
            self.stdout.write(
                f'  - {consultation.id}: {consultation.patient.name} with Dr. {consultation.doctor.name}'
                f' (scheduled: {consultation.scheduled_date} {consultation.scheduled_time}, '
                f'{hours_overdue:.1f} hours overdue)'
            )
        
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nDRY RUN: Would mark {len(overdue_list)} consultation(s) as completed'
                )
            )
            return
        
        # Confirm before proceeding
        confirm = input(f'\nProceed to mark {len(overdue_list)} consultation(s) as completed? (y/N): ')
        if confirm.lower() != 'y':
            self.stdout.write(
                self.style.WARNING('Operation cancelled by user')
            )
            return
        
        # Update consultations
        updated_count = 0
        with transaction.atomic():
            for item in overdue_list:
                consultation = item['consultation']
                
                try:
                    # Update consultation status
                    consultation.status = 'completed'
                    
                    # Set actual end time if not already set
                    if not consultation.actual_end_time:
                        consultation.actual_end_time = timezone.now()
                    
                    consultation.save()
                    updated_count += 1
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ Marked {consultation.id} as completed'
                        )
                    )
                    
                    # Log the action
                    logger.info(
                        f'Auto-completed consultation {consultation.id} '
                        f'(patient: {consultation.patient.name}, doctor: {consultation.doctor.name}) '
                        f'after {item["hours_overdue"]:.1f} hours overdue'
                    )
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'✗ Failed to update {consultation.id}: {str(e)}'
                        )
                    )
                    logger.error(
                        f'Failed to auto-complete consultation {consultation.id}: {str(e)}'
                    )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully marked {updated_count} consultation(s) as completed!'
            )
        )
