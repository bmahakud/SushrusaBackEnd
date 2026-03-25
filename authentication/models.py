from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
import uuid


class UserManager(BaseUserManager):
    """Custom user manager for phone-based authentication"""
    
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError('The Phone field must be set')
        
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'superadmin')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(phone, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model with phone-based authentication"""
    
    ROLE_CHOICES = [
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
        ('admin', 'Admin'),
        ('superadmin', 'Super Admin'),
    ]
    
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    
    id = models.CharField(max_length=20, primary_key=True, unique=True, editable=False)
    phone = models.CharField(validators=[phone_regex], max_length=17, unique=True)
    email = models.EmailField(blank=True, null=True)
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='patient')
    
    # Profile fields
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    
    # Address fields
    street = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    country = models.CharField(max_length=100, default='India')
    
    # Emergency contact
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=17, blank=True)
    emergency_contact_relationship = models.CharField(max_length=50, blank=True)
    
    # Medical information (for patients)
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')
    ]
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES, blank=True)
    allergies = models.TextField(blank=True)
    medical_history = models.TextField(blank=True)
    
    # Status and timestamps
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['name']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def save(self, *args, **kwargs):
        # Normalize phone number to +91XXXXXXXXXX format
        if self.phone:
            from .utils import format_phone_number
            self.phone = format_phone_number(self.phone)
        if not self.id:
            # Generate user ID based on role
            if self.role == 'patient':
                prefix = 'PAT'
            elif self.role == 'doctor':
                prefix = 'DOC'
            elif self.role == 'admin':
                prefix = 'ADM'
            else:
                prefix = 'USR'
            # Get the last user with this prefix
            last_user = User.objects.filter(id__startswith=prefix).order_by('id').last()
            if last_user:
                last_number = int(last_user.id[3:])
                new_number = last_number + 1
            else:
                new_number = 1
            self.id = f"{prefix}{new_number:03d}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} ({self.phone})"
    
    @property
    def full_address(self):
        """Return formatted full address"""
        address_parts = [self.street, self.city, self.state, self.pincode, self.country]
        return ', '.join([part for part in address_parts if part])
    
    @property
    def age(self):
        """Calculate age from date of birth"""
        if self.date_of_birth:
            today = timezone.now().date()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None


class OTP(models.Model):
    """Model to store OTP for phone verification"""
    
    phone = models.CharField(max_length=17)
    otp = models.CharField(max_length=64)
    purpose = models.CharField(max_length=20, choices=[
        ('login', 'Login'),
        ('registration', 'Registration'),
        ('password_reset', 'Password Reset'),
    ], default='login')
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        db_table = 'otps'
        verbose_name = 'OTP'
        verbose_name_plural = 'OTPs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"OTP for {self.phone} - {self.otp}"
    
    @property
    def is_expired(self):
        """Check if OTP is expired"""
        return timezone.now() > self.expires_at
    
    @property
    def is_valid(self):
        """Check if OTP is valid (not used and not expired)"""
        return not self.is_used and not self.is_expired
    @property
    def has_patient_profile(self):
        """Check if user has an active PatientProfile"""
        if self.role != 'patient':
            return False
        return hasattr(self, 'patient_profile') and self.patient_profile.is_active
    
    @property
    def is_complete_patient(self):
        """Check if patient account is complete (has profile)"""
        return self.role == 'patient' and self.has_patient_profile



class UserSession(models.Model):
    """Model to track user sessions and refresh tokens"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    refresh_token = models.TextField()
    device_info = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_sessions'
        verbose_name = 'User Session'
        verbose_name_plural = 'User Sessions'
        ordering = ['-last_used']
    
    def __str__(self):
        return f"Session for {self.user.name} - {self.device_info}"

