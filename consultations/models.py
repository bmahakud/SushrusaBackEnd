from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
from eclinic.models import Clinic
from datetime import timedelta
import datetime
from django.core.exceptions import ValidationError


class Consultation(models.Model):
    """Main consultation model"""
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('patient_checked_in', 'Patient Checked In'),
        ('ready_for_consultation', 'Ready for Consultation'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
        ('rescheduled', 'Rescheduled'),
        ('overdue', 'Overdue'),  # New status for overdue consultations
    ]
    
    CONSULTATION_TYPES = [
        ('video_call', 'Video Call'),
    ]
    
    id = models.CharField(max_length=20, primary_key=True, unique=True, editable=False)
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='patient_consultations'
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='doctor_consultations'
    )
    clinic = models.ForeignKey(
        Clinic,
        on_delete=models.CASCADE,
        related_name='consultations',
        null=True,
        blank=True
    )
    
    # Scheduling Information
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    duration = models.PositiveIntegerField(default=30, help_text="Duration in minutes")
    consultation_type = models.CharField(max_length=20, choices=CONSULTATION_TYPES, default='video_call')
    
    # Consultation Details
    chief_complaint = models.TextField(help_text="Main reason for consultation")
    symptoms = models.TextField(blank=True)
    
    # Status and Progress
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='scheduled')
    actual_start_time = models.DateTimeField(null=True, blank=True)
    actual_end_time = models.DateTimeField(null=True, blank=True)
    
    # Check-in Information
    checked_in_at = models.DateTimeField(null=True, blank=True, help_text="When patient was checked in")
    checked_in_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='check_ins_performed',
        help_text="Admin who checked in the patient"
    )
    ready_for_consultation_at = models.DateTimeField(null=True, blank=True, help_text="When patient was marked ready for consultation")
    ready_marked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='ready_markings_performed',
        help_text="Admin who marked patient as ready"
    )
    
    # Fees and Payment
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=50, blank=True)
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Follow-up
    is_follow_up = models.BooleanField(default=False)
    parent_consultation = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='follow_ups'
    )
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateField(null=True, blank=True)
    
    # Notes and Observations
    doctor_notes = models.TextField(blank=True)
    patient_notes = models.TextField(blank=True)
    prescription_given = models.BooleanField(default=False)
    
    # Cancellation
    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='cancelled_consultations'
    )
    cancellation_reason = models.TextField(blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    # Slot relationship
    booked_slot = models.ForeignKey(
        'doctors.DoctorSlot',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='booked_consultations'
    )
    
    # Reschedule Information
    reschedule_requested = models.BooleanField(default=False, help_text="Whether reschedule has been requested")
    reschedule_requested_at = models.DateTimeField(null=True, blank=True, help_text="When reschedule was requested")
    reschedule_requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='reschedule_requests_made',
        help_text="Who requested the reschedule"
    )
    reschedule_reason = models.TextField(blank=True, help_text="Reason for reschedule request")
    reschedule_approved = models.BooleanField(default=False, help_text="Whether reschedule has been approved")
    reschedule_approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='reschedule_approvals_given',
        help_text="Who approved the reschedule"
    )
    reschedule_approved_at = models.DateTimeField(null=True, blank=True, help_text="When reschedule was approved")
    rescheduled_at = models.DateTimeField(null=True, blank=True, help_text="When reschedule was applied")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'consultations'
        verbose_name = 'Consultation'
        verbose_name_plural = 'Consultations'
        ordering = ['-scheduled_date', '-scheduled_time']
    
    def save(self, *args, **kwargs):
        if not self.id:
            # Generate consultation ID
            last_consultation = Consultation.objects.order_by('id').last()
            if last_consultation:
                # Handle different ID formats safely
                try:
                    if last_consultation.id.startswith('CON'):
                        last_number = int(last_consultation.id[3:])
                    else:
                        # If it doesn't start with CON, find the highest CON number
                        con_consultations = Consultation.objects.filter(id__startswith='CON').order_by('id')
                        if con_consultations.exists():
                            last_con = con_consultations.last()
                            last_number = int(last_con.id[3:])
                        else:
                            last_number = 0
                    new_number = last_number + 1
                except (ValueError, IndexError):
                    # If parsing fails, start from 1
                    new_number = 1
            else:
                new_number = 1
            
            self.id = f"CON{new_number:03d}"
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Consultation {self.id} - {self.patient.name} with Dr. {self.doctor.name}"
    
    @property
    def scheduled_datetime(self):
        """Get scheduled datetime"""
        dt = datetime.datetime.combine(self.scheduled_date, self.scheduled_time)
        # Ensure the datetime is timezone-aware to compare with timezone.now()
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt, timezone.get_current_timezone())
        return dt
    
    @property
    def actual_duration(self):
        """Calculate actual duration in minutes"""
        if self.actual_start_time and self.actual_end_time:
            duration = self.actual_end_time - self.actual_start_time
            return int(duration.total_seconds() / 60)
        return None
    
    @property
    def is_upcoming(self):
        """Check if consultation is upcoming"""
        return self.scheduled_datetime > timezone.now() and self.status == 'scheduled'
    
    @property
    def is_overdue(self):
        """Check if consultation is overdue"""
        if self.status in ['completed', 'cancelled', 'rescheduled']:
            return False
        return self.scheduled_datetime < timezone.now()
    
    @property
    def is_eligible_for_reschedule(self):
        """Check if consultation is eligible for reschedule"""
        # Can reschedule if not completed/cancelled and either overdue or within grace period
        if self.status in ['completed', 'cancelled']:
            return False
        
        # Allow reschedule if overdue or within 1 hour of scheduled time
        grace_period = timezone.now() - timedelta(hours=1)
        return self.scheduled_datetime < grace_period
    
    @property
    def hours_overdue(self):
        """Calculate how many hours the consultation is overdue"""
        if not self.is_overdue:
            return 0
        duration = timezone.now() - self.scheduled_datetime
        return duration.total_seconds() / 3600
    
    def request_reschedule(self, requested_by, reason=""):
        """Request a reschedule for the consultation"""
        if not self.is_eligible_for_reschedule:
            raise ValidationError("This consultation is not eligible for reschedule")
        
        self.reschedule_requested = True
        self.reschedule_requested_at = timezone.now()
        self.reschedule_requested_by = requested_by
        self.reschedule_reason = reason
        self.status = 'overdue'  # Mark as overdue when reschedule is requested
        self.save()
        
        return True
    
    def approve_reschedule(self, approved_by):
        """Approve a reschedule request"""
        if not self.reschedule_requested:
            raise ValidationError("No reschedule request to approve")
        
        self.reschedule_approved = True
        self.reschedule_approved_by = approved_by
        self.reschedule_approved_at = timezone.now()
        self.save()
        
        return True
    
    def apply_reschedule(self, new_date, new_time, reason=""):
        """Apply the reschedule with new date and time"""
        if not self.reschedule_approved:
            raise ValidationError("Reschedule must be approved before applying")
        
        # Store old schedule
        old_date = self.scheduled_date
        old_time = self.scheduled_time
        
        # Update consultation
        self.scheduled_date = new_date
        self.scheduled_time = new_time
        self.status = 'rescheduled'
        self.reschedule_requested = False
        self.reschedule_approved = False
        self.reschedule_requested_at = None
        self.reschedule_approved_at = None
        self.rescheduled_at = timezone.now()
        self.reschedule_reason = ""
        self.save()
        
        # Create reschedule record
        ConsultationReschedule.objects.create(
            consultation=self,
            old_date=old_date,
            old_time=old_time,
            new_date=new_date,
            new_time=new_time,
            reason=reason,
            requested_by=self.reschedule_requested_by
        )
        
        return True
    
    @property
    def is_checked_in(self):
        """Check if patient is checked in"""
        return self.status in ['patient_checked_in', 'ready_for_consultation', 'in_progress', 'completed']
    
    @property
    def is_ready_for_consultation(self):
        """Check if patient is ready for consultation"""
        return self.status in ['ready_for_consultation', 'in_progress', 'completed']
    
    def check_in_patient(self, checked_in_by):
        """Mark patient as checked in"""
        if self.status == 'scheduled':
            self.status = 'patient_checked_in'
            self.checked_in_at = timezone.now()
            self.checked_in_by = checked_in_by
            self.save()
            return True
        return False
    
    def mark_ready_for_consultation(self, marked_by):
        """Mark patient as ready for consultation"""
        if self.status in ['scheduled', 'patient_checked_in']:
            self.status = 'ready_for_consultation'
            self.ready_for_consultation_at = timezone.now()
            self.ready_marked_by = marked_by
            self.save()
            return True
        return False
    
    def start_consultation(self):
        """Start the consultation"""
        if self.status in ['ready_for_consultation', 'patient_checked_in']:
            self.status = 'in_progress'
            self.actual_start_time = timezone.now()
            self.save()
            return True
        return False


class ConsultationSymptom(models.Model):
    """Symptoms recorded during consultation"""
    
    consultation = models.ForeignKey(
        Consultation, 
        on_delete=models.CASCADE, 
        related_name='recorded_symptoms'
    )
    symptom = models.CharField(max_length=200)
    severity = models.CharField(max_length=20, choices=[
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe'),
    ], default='mild')
    duration = models.CharField(max_length=100, blank=True, help_text="How long has this symptom persisted")
    notes = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'consultation_symptoms'
        verbose_name = 'Consultation Symptom'
        verbose_name_plural = 'Consultation Symptoms'
    
    def __str__(self):
        return f"{self.symptom} - {self.consultation.id}"


class ConsultationDiagnosis(models.Model):
    """Diagnoses made during consultation"""
    
    DIAGNOSIS_TYPES = [
        ('primary', 'Primary'),
        ('secondary', 'Secondary'),
        ('differential', 'Differential'),
        ('provisional', 'Provisional'),
    ]
    
    consultation = models.ForeignKey(
        Consultation, 
        on_delete=models.CASCADE, 
        related_name='diagnoses'
    )
    diagnosis = models.CharField(max_length=300)
    diagnosis_type = models.CharField(max_length=20, choices=DIAGNOSIS_TYPES, default='primary')
    icd_code = models.CharField(max_length=20, blank=True, help_text="ICD-10 code")
    notes = models.TextField(blank=True)
    confidence_level = models.CharField(max_length=20, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ], default='medium')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'consultation_diagnoses'
        verbose_name = 'Consultation Diagnosis'
        verbose_name_plural = 'Consultation Diagnoses'
    
    def __str__(self):
        return f"{self.diagnosis} - {self.consultation.id}"


class ConsultationVitalSigns(models.Model):
    """Vital signs recorded during consultation"""
    
    consultation = models.OneToOneField(
        Consultation, 
        on_delete=models.CASCADE, 
        related_name='vital_signs'
    )
    
    # Basic vitals
    blood_pressure_systolic = models.PositiveIntegerField(null=True, blank=True)
    blood_pressure_diastolic = models.PositiveIntegerField(null=True, blank=True)
    heart_rate = models.PositiveIntegerField(null=True, blank=True, help_text="BPM")
    temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, help_text="Celsius")
    respiratory_rate = models.PositiveIntegerField(null=True, blank=True, help_text="Per minute")
    oxygen_saturation = models.PositiveIntegerField(null=True, blank=True, help_text="Percentage")
    
    # Physical measurements
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="cm")
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="kg")
    bmi = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    
    # Additional measurements
    blood_glucose = models.PositiveIntegerField(null=True, blank=True, help_text="mg/dL")
    notes = models.TextField(blank=True)
    
    # Metadata
    recorded_at = models.DateTimeField(auto_now_add=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    class Meta:
        db_table = 'consultation_vital_signs'
        verbose_name = 'Consultation Vital Signs'
        verbose_name_plural = 'Consultation Vital Signs'
    
    def __str__(self):
        return f"Vitals for {self.consultation.id}"
    
    def save(self, *args, **kwargs):
        # Calculate BMI if height and weight are provided
        if self.height and self.weight:
            height_m = self.height / 100  # Convert cm to meters
            self.bmi = self.weight / (height_m * height_m)
        super().save(*args, **kwargs)


class ConsultationAttachment(models.Model):
    """Files and documents attached to consultation"""
    
    ATTACHMENT_TYPES = [
        ('image', 'Image'),
        ('document', 'Document'),
        ('lab_report', 'Lab Report'),
        ('prescription', 'Prescription'),
        ('xray', 'X-Ray'),
        ('scan', 'Scan'),
        ('other', 'Other'),
    ]
    
    consultation = models.ForeignKey(
        Consultation, 
        on_delete=models.CASCADE, 
        related_name='attachments'
    )
    file = models.FileField(upload_to='consultation_attachments/')
    attachment_type = models.CharField(max_length=20, choices=ATTACHMENT_TYPES, default='document')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Uploaded by
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE
    )
    
    # Metadata
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'consultation_attachments'
        verbose_name = 'Consultation Attachment'
        verbose_name_plural = 'Consultation Attachments'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.title} - {self.consultation.id}"


class ConsultationNote(models.Model):
    """Additional notes during consultation"""
    
    NOTE_TYPES = [
        ('general', 'General'),
        ('examination', 'Examination'),
        ('treatment', 'Treatment'),
        ('advice', 'Advice'),
        ('follow_up', 'Follow-up'),
    ]
    
    consultation = models.ForeignKey(
        Consultation, 
        on_delete=models.CASCADE, 
        related_name='notes'
    )
    note_type = models.CharField(max_length=20, choices=NOTE_TYPES, default='general')
    content = models.TextField()
    
    # Author
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'consultation_notes'
        verbose_name = 'Consultation Note'
        verbose_name_plural = 'Consultation Notes'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.note_type} note for {self.consultation.id}"


class ConsultationReschedule(models.Model):
    """Track consultation reschedule history"""
    
    consultation = models.ForeignKey(
        Consultation, 
        on_delete=models.CASCADE, 
        related_name='reschedule_history'
    )
    old_date = models.DateField()
    old_time = models.TimeField()
    new_date = models.DateField()
    new_time = models.TimeField()
    reason = models.TextField()
    
    # Who requested the reschedule
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'consultation_reschedules'
        verbose_name = 'Consultation Reschedule'
        verbose_name_plural = 'Consultation Reschedules'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Reschedule for {self.consultation.id} - {self.old_date} to {self.new_date}"


class ConsultationReceipt(models.Model):
    """Receipt for consultation payments"""
    
    consultation = models.OneToOneField(
        Consultation, 
        on_delete=models.CASCADE, 
        related_name='receipt'
    )
    
    # Receipt details
    receipt_number = models.CharField(max_length=50, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    payment_status = models.CharField(max_length=20)
    
    # Issued by
    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='issued_receipts'
    )
    
    # Receipt content
    receipt_content = models.JSONField(default=dict, help_text="Receipt details in JSON format")
    
    # Metadata
    issued_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'consultation_receipts'
        verbose_name = 'Consultation Receipt'
        verbose_name_plural = 'Consultation Receipts'
        ordering = ['-issued_at']
    
    def save(self, *args, **kwargs):
        if not self.receipt_number:
            # Generate receipt number
            last_receipt = ConsultationReceipt.objects.order_by('id').last()
            if last_receipt:
                last_number = int(last_receipt.receipt_number[3:])
                new_number = last_number + 1
            else:
                new_number = 1
            
            self.receipt_number = f"RCP{new_number:06d}"
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Receipt {self.receipt_number} - {self.consultation.id}"
    
    @property
    def formatted_amount(self):
        """Get formatted amount with currency"""
        return f"₹{self.amount}"
    
    @property
    def receipt_data(self):
        """Get formatted receipt data"""
        consultation = self.consultation
        return {
            'receipt_number': self.receipt_number,
            'consultation_id': consultation.id,
            'patient_name': consultation.patient.name,
            'doctor_name': consultation.doctor.name,
            'clinic_name': consultation.clinic.name if consultation.clinic else 'N/A',
            'consultation_date': consultation.scheduled_date,
            'consultation_time': consultation.scheduled_time,
            'consultation_type': consultation.consultation_type,
            'amount': self.formatted_amount,
            'payment_method': self.payment_method,
            'payment_status': self.payment_status,
            'issued_by': self.issued_by.name,
            'issued_at': self.issued_at,
            'chief_complaint': consultation.chief_complaint,
        }

