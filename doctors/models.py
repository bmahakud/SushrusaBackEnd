from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import json


class DoctorProfile(models.Model):
    """Extended profile for doctors"""
    
    SPECIALTIES = [
        ('Cardiology', 'Cardiology'),
        ('Dermatology', 'Dermatology'),
        ('Endocrinology', 'Endocrinology'),
        ('Gastroenterology', 'Gastroenterology'),
        ('General Medicine', 'General Medicine'),
        ('Gynecology', 'Gynecology'),
        ('Neurology', 'Neurology'),
        ('Oncology', 'Oncology'),
        ('Ophthalmology', 'Ophthalmology'),
        ('Orthopedics', 'Orthopedics'),
        ('Pediatrics', 'Pediatrics'),
        ('Psychiatry', 'Psychiatry'),
        ('Pulmonology', 'Pulmonology'),
        ('Radiology', 'Radiology'),
        ('Surgery', 'Surgery'),
        ('Urology', 'Urology'),
        ('Other', 'Other'),
    ]
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='doctor_profile'
    )
    
    # Professional Information
    license_number = models.CharField(max_length=50, unique=True)
    qualification = models.CharField(max_length=200)
    specialization = models.CharField(max_length=50, choices=SPECIALTIES)
    sub_specialization = models.CharField(max_length=100, blank=True)
    experience_years = models.PositiveIntegerField()
    
    # Consultation Information
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2)
    consultation_duration = models.PositiveIntegerField(
        default=5, 
        help_text="Duration in minutes",
        validators=[MinValueValidator(5), MaxValueValidator(15)]
    )
    
    # Ratings and Reviews
    rating = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )
    total_reviews = models.PositiveIntegerField(default=0)
    
    # Clinic Information
    clinic_name = models.CharField(max_length=200, blank=True)
    clinic_address = models.TextField(blank=True)
    
    # Online Consultation
    is_online_consultation_available = models.BooleanField(default=True)
    online_consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Languages
    languages_spoken = models.JSONField(default=list, help_text="List of languages spoken")
    
    # Bio and Description
    bio = models.TextField(blank=True)
    achievements = models.TextField(blank=True)
    
    # Status
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_accepting_patients = models.BooleanField(default=True)
    
    # Personal Information
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_anniversary = models.DateField(null=True, blank=True)
    
    # Digital Signature
    signature = models.FileField(
        upload_to='doctor_signatures/',
        null=True,
        blank=True,
        help_text="Doctor's digital signature file"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'doctor_profiles'
        verbose_name = 'Doctor Profile'
        verbose_name_plural = 'Doctor Profiles'
    
    def __str__(self):
        return f"Dr. {self.user.name} - {self.specialization}"
    
    @property
    def total_consultations(self):
        """Get total number of consultations"""
        return self.user.doctor_consultations.count()
    
    @property
    def completed_consultations(self):
        """Get number of completed consultations"""
        return self.user.doctor_consultations.filter(status='completed').count()

    @property
    def meeting_link(self):
        # Use the user's unique id (e.g., DOC001) for the meeting link
        return f"https://meet.diracai.com/{self.user.id}"


class DoctorSchedule(models.Model):
    """Weekly schedule for doctors"""
    
    DAYS_OF_WEEK = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]
    
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='schedules'
    )
    day_of_week = models.CharField(max_length=10, choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    
    # Break times
    break_start_time = models.TimeField(null=True, blank=True)
    break_end_time = models.TimeField(null=True, blank=True)
    break_reason = models.CharField(max_length=100, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'doctor_schedules'
        verbose_name = 'Doctor Schedule'
        verbose_name_plural = 'Doctor Schedules'
        unique_together = ['doctor', 'day_of_week']
    
    def __str__(self):
        return f"{self.doctor.name} - {self.day_of_week} ({self.start_time}-{self.end_time})"


class DoctorSlot(models.Model):
    """Specific time slots for doctor availability (supports multiple slots per day, calendar/month view)"""
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='slots'
    )
    clinic = models.ForeignKey(
        'eclinic.Clinic',
        on_delete=models.CASCADE,
        related_name='doctor_slots',
        help_text="Clinic for which this slot is created",
        null=True,
        blank=True
    )
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    is_booked = models.BooleanField(default=False, help_text="Whether this slot is booked for a consultation")
    booked_consultation = models.ForeignKey(
        'consultations.Consultation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='booked_slots'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'doctor_slots'
        verbose_name = 'Doctor Slot'
        verbose_name_plural = 'Doctor Slots'
        unique_together = ['doctor', 'clinic', 'date', 'start_time', 'end_time']
        ordering = ['date', 'start_time']

    def __str__(self):
        status = "Available" if self.is_available else "Unavailable"
        return f"{self.doctor.name} - {self.date} {self.start_time}-{self.end_time} ({status})"

    @classmethod
    def generate_slots_for_availability(cls, doctor, clinic, date, start_time, end_time):
        """
        Generate individual consultation slots based on doctor availability and clinic consultation duration
        
        Args:
            doctor: Doctor user object
            clinic: Clinic object
            date: Date for which slots are to be generated
            start_time: Start time of availability (time object)
            end_time: End time of availability (time object)
        
        Returns:
            List of created DoctorSlot objects
        """
        from datetime import datetime, timedelta
        
        # Get clinic consultation duration
        consultation_duration = clinic.consultation_duration  # in minutes
        
        # Convert times to datetime for easier manipulation
        start_datetime = datetime.combine(date, start_time)
        end_datetime = datetime.combine(date, end_time)
        
        slots = []
        current_time = start_datetime
        
        while current_time < end_datetime:
            slot_end_time = current_time + timedelta(minutes=consultation_duration)
            
            # Don't create slot if it would exceed the end time
            if slot_end_time > end_datetime:
                break
            
            # Create slot
            slot = cls.objects.create(
                doctor=doctor,
                clinic=clinic,
                date=date,
                start_time=current_time.time(),
                end_time=slot_end_time.time(),
                is_available=True,
                is_booked=False
            )
            slots.append(slot)
            
            # Move to next slot
            current_time = slot_end_time
        
        return slots


class DoctorEducation(models.Model):
    """Education details for doctors"""
    
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='education'
    )
    degree = models.CharField(max_length=100)
    institution = models.CharField(max_length=200)
    year_of_completion = models.PositiveIntegerField()
    grade_or_percentage = models.CharField(max_length=20, blank=True)
    
    # Document
    certificate = models.FileField(upload_to='doctor_certificates/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'doctor_education'
        verbose_name = 'Doctor Education'
        verbose_name_plural = 'Doctor Education'
        ordering = ['-year_of_completion']
    
    def __str__(self):
        return f"{self.doctor.name} - {self.degree} from {self.institution}"


class DoctorExperience(models.Model):
    """Work experience for doctors"""
    
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='experience'
    )
    organization = models.CharField(max_length=200)
    position = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'doctor_experience'
        verbose_name = 'Doctor Experience'
        verbose_name_plural = 'Doctor Experience'
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.doctor.name} - {self.position} at {self.organization}"


class DoctorReview(models.Model):
    """Reviews and ratings for doctors"""
    
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='reviews'
    )
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='given_reviews'
    )
    consultation = models.OneToOneField(
        'consultations.Consultation', 
        on_delete=models.CASCADE, 
        related_name='review',
        null=True, 
        blank=True
    )
    
    # Rating and Review
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    review_text = models.TextField(blank=True)
    
    # Specific ratings
    communication_rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True
    )
    treatment_rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True
    )
    punctuality_rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True
    )
    
    # Status
    is_approved = models.BooleanField(default=True)
    is_anonymous = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'doctor_reviews'
        verbose_name = 'Doctor Review'
        verbose_name_plural = 'Doctor Reviews'
        unique_together = ['doctor', 'patient', 'consultation']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Review for Dr. {self.doctor.name} by {self.patient.name} - {self.rating}/5"


class DoctorDocument(models.Model):
    """Documents for doctor verification"""
    
    DOCUMENT_TYPES = [
        ('license', 'Medical License'),
        ('degree_certificate', 'Degree Certificate'),
        ('experience_certificate', 'Experience Certificate'),
        ('id_proof', 'ID Proof'),
        ('address_proof', 'Address Proof'),
        ('other', 'Other'),
    ]
    
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='doctor_documents'
    )
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='doctor_documents/')
    
    # Verification status
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='verified_doctor_documents'
    )
    verified_at = models.DateTimeField(blank=True, null=True)
    verification_notes = models.TextField(blank=True)
    
    # Metadata
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'doctor_documents'
        verbose_name = 'Doctor Document'
        verbose_name_plural = 'Doctor Documents'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.title} - Dr. {self.doctor.name}"


class DoctorStatus(models.Model):
    """Model to track real-time doctor status and activity"""
    
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('consulting', 'In Consultation'),
        ('busy', 'Busy'),
        ('away', 'Away'),
        ('offline', 'Offline'),
        ('break', 'On Break'),
        ('unavailable', 'Unavailable')
    ]
    
    doctor = models.OneToOneField('DoctorProfile', on_delete=models.CASCADE, related_name='status')
    is_online = models.BooleanField(default=False, help_text="Whether doctor is currently connected")
    is_logged_in = models.BooleanField(default=False, help_text="Whether doctor is authenticated")
    is_available = models.BooleanField(default=True, help_text="Whether doctor is available for consultations")
    current_status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='offline',
        help_text="Current status of the doctor"
    )
    last_activity = models.DateTimeField(auto_now=True, help_text="Last activity timestamp")
    last_login = models.DateTimeField(null=True, blank=True, help_text="Last login timestamp")
    last_logout = models.DateTimeField(null=True, blank=True, help_text="Last logout timestamp")
    current_consultation = models.ForeignKey(
        'consultations.Consultation', 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL,
        related_name='active_doctor_status',
        help_text="Currently active consultation if any"
    )
    status_updated_at = models.DateTimeField(auto_now=True, help_text="When status was last updated")
    status_note = models.TextField(blank=True, help_text="Optional note about current status")
    auto_away_threshold = models.IntegerField(
        default=15, 
        help_text="Minutes of inactivity before auto-away status"
    )
    
    class Meta:
        verbose_name = "Doctor Status"
        verbose_name_plural = "Doctor Statuses"
        ordering = ['-last_activity']
    
    def __str__(self):
        return f"{self.doctor.name} - {self.current_status}"
    
    @property
    def is_active(self):
        """Check if doctor is currently active (online and available)"""
        return self.is_online and self.is_available and self.current_status in ['available', 'consulting']
    
    @property
    def status_display(self):
        """Get human-readable status with activity time"""
        if self.current_status == 'offline':
            return f"Offline (Last seen: {self.last_activity.strftime('%H:%M')})"
        elif self.current_status == 'away':
            return f"Away (Since: {self.last_activity.strftime('%H:%M')})"
        else:
            return self.get_current_status_display()
    
    def update_status(self, status, note=""):
        """Update doctor status"""
        self.current_status = status
        self.status_note = note
        self.status_updated_at = timezone.now()
        self.save()
    
    def mark_online(self):
        """Mark doctor as online"""
        self.is_online = True
        self.is_logged_in = True
        self.last_login = timezone.now()
        if self.current_status == 'offline':
            self.current_status = 'available'
        self.save()
    
    def mark_offline(self):
        """Mark doctor as offline"""
        self.is_online = False
        self.is_logged_in = False
        self.current_status = 'offline'
        self.last_logout = timezone.now()
        self.current_consultation = None
        self.save()
    
    def start_consultation(self, consultation):
        """Start a consultation"""
        self.current_status = 'consulting'
        self.current_consultation = consultation
        self.is_available = False
        self.save()
    
    def end_consultation(self):
        """End current consultation"""
        self.current_status = 'available'
        self.current_consultation = None
        self.is_available = True
        self.save()
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = timezone.now()
        # Auto-away logic
        if self.is_online and self.current_status == 'available':
            time_diff = timezone.now() - self.last_activity
            if time_diff.total_seconds() > (self.auto_away_threshold * 60):
                self.current_status = 'away'
        self.save()


class DoctorSignature(models.Model):
    """Model to store doctor signature information"""
    
    doctor = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='signature_info'
    )
    
    # Signature file information
    signature_url = models.URLField(help_text="URL to the signature file in cloud storage")
    file_path = models.CharField(max_length=500, help_text="Path to the signature file in storage")
    file_name = models.CharField(max_length=200, help_text="Original filename of the signature")
    file_size = models.PositiveIntegerField(help_text="Size of the signature file in bytes")
    
    # Upload information
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploaded_signatures'
    )
    
    # Status
    is_active = models.BooleanField(default=True, help_text="Whether this signature is currently active")
    
    class Meta:
        db_table = 'doctor_signatures'
        verbose_name = 'Doctor Signature'
        verbose_name_plural = 'Doctor Signatures'
    
    def __str__(self):
        return f"Signature for {self.doctor.name}"
    
    @property
    def signed_url(self):
        """Get signed URL for the signature file"""
        try:
            from utils.signed_urls import get_signed_media_url
            return get_signed_media_url(self.file_path)
        except Exception as e:
            print(f"Error getting signed URL: {e}")
            return self.signature_url

