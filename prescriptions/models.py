from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from consultations.models import Consultation
import uuid
import os

class Prescription(models.Model):
    """Enhanced prescription model matching the comprehensive prescription structure"""
    
    # Basic Information
    consultation = models.ForeignKey(
        Consultation,
        on_delete=models.CASCADE,
        related_name='prescriptions',
        null=True,
        blank=True
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='prescriptions_as_doctor'
    )
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='prescriptions_as_patient'
    )
    
    # Prescription Details
    issued_date = models.DateField(auto_now_add=True)
    issued_time = models.TimeField(auto_now_add=True)
    
    # Patient Vitals (from consultation)
    pulse = models.PositiveIntegerField(null=True, blank=True, help_text="Pulse rate in bpm")
    blood_pressure_systolic = models.PositiveIntegerField(null=True, blank=True, help_text="Systolic BP")
    blood_pressure_diastolic = models.PositiveIntegerField(null=True, blank=True, help_text="Diastolic BP")
    temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, help_text="Temperature in Celsius")
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Weight in kg")
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Height in cm")
    
    # Diagnosis
    primary_diagnosis = models.TextField(blank=True, help_text="Primary diagnosis")
    patient_previous_history = models.TextField(blank=True, help_text="Patient's previous medical history")
    clinical_classification = models.TextField(blank=True, help_text="Clinical classification (e.g., NYHA Class)")
    
    # General Instructions
    general_instructions = models.TextField(blank=True, help_text="General medication instructions")
    fluid_intake = models.CharField(max_length=100, blank=True, help_text="Fluid intake instructions")
    diet_instructions = models.TextField(blank=True, help_text="Diet instructions")
    lifestyle_advice = models.TextField(blank=True, help_text="Lifestyle advice")
    
    # Follow-up
    next_visit = models.CharField(max_length=100, blank=True, help_text="Next visit instructions")
    follow_up_notes = models.TextField(blank=True, help_text="Follow-up notes")
    
    # Prescription Status
    is_draft = models.BooleanField(default=True, help_text="Whether prescription is in draft mode")
    is_finalized = models.BooleanField(default=False, help_text="Whether prescription is finalized")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'prescriptions'
        verbose_name = 'Prescription'
        verbose_name_plural = 'Prescriptions'
        ordering = ['-created_at']
        unique_together = ['consultation', 'doctor', 'patient']

    def __str__(self):
        return f"Prescription for {self.patient.name} by {self.doctor.name} on {self.issued_date}"


def prescription_pdf_upload_path(instance, filename):
    """Generate upload path for prescription PDFs"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    consultation_id = instance.prescription.consultation.id if instance.prescription.consultation else 'no-consultation'
    return os.path.join('prescriptions', 'pdfs', str(consultation_id), filename)


class PrescriptionPDF(models.Model):
    """Model to store finalized prescription PDFs with versioning"""
    
    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        related_name='pdf_versions'
    )
    
    # PDF File
    pdf_file = models.FileField(
        upload_to=prescription_pdf_upload_path,
        help_text="Generated prescription PDF"
    )
    
    # Version information
    version_number = models.PositiveIntegerField(help_text="Version number of this prescription")
    is_current = models.BooleanField(default=True, help_text="Whether this is the current version")
    
    # Generation details
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='generated_prescription_pdfs'
    )
    generated_at = models.DateTimeField(auto_now_add=True)
    is_mobile_generated = models.BooleanField(default=False, help_text="Whether this PDF was generated from mobile consultation")
    
    # Header and Footer used for this PDF
    header_image = models.ImageField(
        upload_to='prescription_headers/',
        null=True,
        blank=True,
        help_text="Header image used for this PDF"
    )
    footer_image = models.ImageField(
        upload_to='prescription_footers/',
        null=True,
        blank=True,
        help_text="Footer image used for this PDF"
    )
    
    # Metadata
    file_size = models.PositiveIntegerField(null=True, blank=True, help_text="File size in bytes")
    checksum = models.CharField(max_length=64, blank=True, help_text="MD5 checksum of the file")
    
    class Meta:
        db_table = 'prescription_pdfs'
        verbose_name = 'Prescription PDF'
        verbose_name_plural = 'Prescription PDFs'
        ordering = ['-version_number', '-generated_at']
        unique_together = ['prescription', 'version_number']
    
    def __str__(self):
        return f"Prescription PDF v{self.version_number} for {self.prescription}"
    
    def save(self, *args, **kwargs):
        # Set version number if not set
        if not self.version_number:
            last_version = PrescriptionPDF.objects.filter(
                prescription=self.prescription
            ).order_by('-version_number').first()
            
            self.version_number = (last_version.version_number + 1) if last_version else 1
        
        # Mark other versions as not current if this is current
        if self.is_current:
            PrescriptionPDF.objects.filter(
                prescription=self.prescription
            ).exclude(
                id=self.id
            ).update(is_current=False)
        
        super().save(*args, **kwargs)

class PrescriptionMedication(models.Model):
    """Individual medications in a prescription"""
    
    FREQUENCY_CHOICES = [
        ('once_daily', 'Once Daily'),
        ('twice_daily', 'Twice Daily'),
        ('thrice_daily', 'Thrice Daily'),
        ('four_times_daily', 'Four Times Daily'),
        ('sos', 'SOS (As Needed)'),
        ('custom', 'Custom'),
    ]
    
    TIMING_CHOICES = [
        ('with_food', 'After Food'),
        ('before_breakfast', 'Before Food'),
        ('empty_stomach', 'Empty Stomach'),
        ('bedtime', 'Bedtime'),
        # Legacy options for backward compatibility
        ('after_breakfast', 'After Breakfast'),
        ('before_lunch', 'Before Lunch'),
        ('after_lunch', 'After Lunch'),
        ('before_dinner', 'Before Dinner'),
        ('after_dinner', 'After Dinner'),
        ('custom', 'Custom'),
    ]
    
    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        related_name='medications'
    )
    
    # Medication Details
    medicine_name = models.CharField(max_length=200, help_text="Name of the medicine")
    composition = models.CharField(max_length=500, blank=True, help_text="Composition/ingredients")
    dosage_form = models.CharField(max_length=100, blank=True, help_text="Tablet, Syrup, Injection, etc.")
    
    # Dosage (Morning-Afternoon-Night format like 1-0-1)
    morning_dose = models.PositiveIntegerField(default=0, help_text="Morning dose")
    afternoon_dose = models.PositiveIntegerField(default=0, help_text="Afternoon dose")
    evening_dose = models.PositiveIntegerField(default=0, help_text="Evening dose")
    
    # Timing and Frequency
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='once_daily')
    timing = models.CharField(max_length=20, choices=TIMING_CHOICES, default='with_food')
    custom_timing = models.CharField(max_length=200, blank=True, help_text="Custom timing instructions")
    timing_display_text = models.CharField(max_length=200, blank=True, help_text="Human-readable timing display text (e.g., Before Breakfast, Lunch & Dinner)")
    
    # Duration
    duration_days = models.PositiveIntegerField(null=True, blank=True, help_text="Duration in days")
    duration_weeks = models.PositiveIntegerField(null=True, blank=True, help_text="Duration in weeks")
    duration_months = models.PositiveIntegerField(null=True, blank=True, help_text="Duration in months")
    is_continuous = models.BooleanField(default=False, help_text="Continue indefinitely")
    
    # Quantity
    quantity = models.CharField(max_length=100, blank=True, help_text="Quantity (e.g., 10 tablets, 1 bottle)")
    
    # Special Instructions
    special_instructions = models.TextField(blank=True, help_text="Special instructions for this medication")
    notes = models.TextField(blank=True, help_text="Additional notes")
    
    # Order
    order = models.PositiveIntegerField(default=0, help_text="Order of medication in prescription")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'prescription_medications'
        verbose_name = 'Prescription Medication'
        verbose_name_plural = 'Prescription Medications'
        ordering = ['order', 'created_at']

    def get_timing_display(self):
        """Get human-readable timing display with legacy mapping"""
        # Map legacy values to simplified labels
        legacy_mapping = {
            'after_breakfast': 'After Food',
            'after_lunch': 'After Food',
            'after_dinner': 'After Food',
            'before_lunch': 'Before Food',
            'before_dinner': 'Before Food',
        }
        
        if self.timing in legacy_mapping:
            return legacy_mapping[self.timing]
        
        timing_map = dict(self.TIMING_CHOICES)
        return timing_map.get(self.timing, self.timing)
    
    def get_frequency_display(self):
        """Get human-readable frequency display"""
        frequency_map = dict(self.FREQUENCY_CHOICES)
        return frequency_map.get(self.frequency, self.frequency)

    def __str__(self):
        return f"{self.medicine_name} - {self.prescription}"

class PrescriptionVitalSigns(models.Model):
    """Vital signs recorded during prescription"""
    
    prescription = models.OneToOneField(
        Prescription,
        on_delete=models.CASCADE,
        related_name='vital_signs'
    )
    
    # Vital Signs
    pulse = models.PositiveIntegerField(null=True, blank=True, help_text="Pulse rate in bpm")
    blood_pressure_systolic = models.PositiveIntegerField(null=True, blank=True, help_text="Systolic BP")
    blood_pressure_diastolic = models.PositiveIntegerField(null=True, blank=True, help_text="Diastolic BP")
    temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, help_text="Temperature in Celsius")
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Weight in kg")
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Height in cm")
    respiratory_rate = models.PositiveIntegerField(null=True, blank=True, help_text="Respiratory rate per minute")
    oxygen_saturation = models.PositiveIntegerField(
        null=True, 
        blank=True, 
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Oxygen saturation percentage"
    )
    
    # Additional Vitals
    blood_sugar_fasting = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Fasting blood sugar")
    blood_sugar_postprandial = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Postprandial blood sugar")
    hba1c = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, help_text="HbA1c percentage")
    
    # Notes
    notes = models.TextField(blank=True, help_text="Additional notes about vital signs")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'prescription_vital_signs'
        verbose_name = 'Prescription Vital Signs'
        verbose_name_plural = 'Prescription Vital Signs'

    def __str__(self):
        return f"Vital Signs for {self.prescription}"


class InvestigationCategory(models.Model):
    """Categories for different types of investigations/tests"""
    
    name = models.CharField(max_length=100, unique=True, help_text="Category name (e.g., Blood Tests, Imaging, etc.)")
    description = models.TextField(blank=True, help_text="Description of the category")
    is_active = models.BooleanField(default=True, help_text="Whether this category is active")
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'investigation_categories'
        verbose_name = 'Investigation Category'
        verbose_name_plural = 'Investigation Categories'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class InvestigationTest(models.Model):
    """Individual investigation tests that doctors can prescribe"""
    
    category = models.ForeignKey(
        InvestigationCategory,
        on_delete=models.CASCADE,
        related_name='tests'
    )
    
    # Test Details
    name = models.CharField(max_length=200, help_text="Name of the test")
    code = models.CharField(max_length=50, blank=True, help_text="Test code/abbreviation")
    description = models.TextField(blank=True, help_text="Description of what the test measures")
    normal_range = models.CharField(max_length=200, blank=True, help_text="Normal range values")
    unit = models.CharField(max_length=50, blank=True, help_text="Unit of measurement")
    
    # Test Properties
    is_fasting_required = models.BooleanField(default=False, help_text="Whether fasting is required")
    preparation_instructions = models.TextField(blank=True, help_text="Patient preparation instructions")
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Estimated cost of the test")
    
    # Status
    is_active = models.BooleanField(default=True, help_text="Whether this test is available")
    order = models.PositiveIntegerField(default=0, help_text="Display order within category")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'investigation_tests'
        verbose_name = 'Investigation Test'
        verbose_name_plural = 'Investigation Tests'
        ordering = ['category__order', 'order', 'name']
        unique_together = ['category', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.category.name})"


class PrescriptionInvestigation(models.Model):
    """Investigation tests prescribed in a prescription"""
    
    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        related_name='investigations'
    )
    
    test = models.ForeignKey(
        InvestigationTest,
        on_delete=models.CASCADE,
        related_name='prescriptions'
    )
    
    # Prescription Details
    priority = models.CharField(
        max_length=20,
        choices=[
            ('routine', 'Routine'),
            ('urgent', 'Urgent'),
            ('emergency', 'Emergency'),
        ],
        default='routine',
        help_text="Priority level of the test"
    )
    
    # Instructions
    special_instructions = models.TextField(blank=True, help_text="Special instructions for this test")
    notes = models.TextField(blank=True, help_text="Additional notes")
    
    # Order
    order = models.PositiveIntegerField(default=0, help_text="Order of investigation in prescription")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'prescription_investigations'
        verbose_name = 'Prescription Investigation'
        verbose_name_plural = 'Prescription Investigations'
        ordering = ['order', 'created_at']
        unique_together = ['prescription', 'test']
    
    def __str__(self):
        return f"{self.test.name} for {self.prescription}"


class PrescriptionImage(models.Model):
    """Model to store prescription images uploaded from mobile"""
    
    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        related_name='prescription_images'
    )
    image_file = models.ImageField(
        upload_to='prescriptions/images/',
        help_text="Prescription image uploaded from mobile"
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='uploaded_prescription_images'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_mobile_upload = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Prescription Image'
        verbose_name_plural = 'Prescription Images'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"Image for {self.prescription} uploaded by {self.uploaded_by}"


