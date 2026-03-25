from django.core.management.base import BaseCommand
from django.utils import timezone
from consultations.models import Consultation
from payments.models import Payment
import uuid


class Command(BaseCommand):
    help = 'Create payment records for consultations that don\'t have corresponding payment records'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without actually creating records',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Find consultations without payment records
        consultations_without_payments = Consultation.objects.filter(
            payments__isnull=True
        ).distinct()
        
        self.stdout.write(f"Found {consultations_without_payments.count()} consultations without payment records")
        
        if dry_run:
            self.stdout.write("DRY RUN - No records will be created")
        
        created_count = 0
        error_count = 0
        
        for consultation in consultations_without_payments:
            try:
                if not dry_run:
                    # Generate payment ID
                    payment_id = f"PAY{uuid.uuid4().hex[:12].upper()}"
                    
                    # Create payment record
                    payment = Payment.objects.create(
                        id=payment_id,
                        patient=consultation.patient,
                        doctor=consultation.doctor,
                        consultation=consultation,
                        amount=consultation.consultation_fee,
                        currency='INR',
                        payment_type='consultation',
                        description=f"Consultation fee for {consultation.consultation_type}",
                        payment_method=consultation.payment_method or 'cash',
                        status='completed' if consultation.payment_status == 'paid' else 'pending',
                        net_amount=consultation.consultation_fee,
                        platform_fee=0,
                        gateway_fee=0,
                        tax_amount=0,
                        discount_amount=0,
                        processed_at=timezone.now() if consultation.payment_status == 'paid' else None,
                        completed_at=timezone.now() if consultation.payment_status == 'paid' else None,
                        receipt_number=f"RCP{payment_id}"
                    )
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Created payment record {payment_id} for consultation {consultation.id}"
                        )
                    )
                else:
                    self.stdout.write(
                        f"Would create payment record for consultation {consultation.id} "
                        f"(Patient: {consultation.patient.name}, "
                        f"Doctor: {consultation.doctor.name}, "
                        f"Amount: ₹{consultation.consultation_fee}, "
                        f"Status: {consultation.payment_status})"
                    )
                
                created_count += 1
                
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(
                        f"Error creating payment record for consultation {consultation.id}: {str(e)}"
                    )
                )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"DRY RUN COMPLETED: Would create {created_count} payment records"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"COMPLETED: Created {created_count} payment records, {error_count} errors"
                )
            ) 