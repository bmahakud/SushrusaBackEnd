
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
    
    def patients_with_profiles(self):
        """Return only patients who have active PatientProfile"""
        return self.filter(role='patient', patient_profile__isnull=False, patient_profile__is_active=True)
    
    def patients_without_profiles(self):
        """Return patients who don't have PatientProfile"""
        return self.filter(role='patient', patient_profile__isnull=True)
    
    def active_patients(self):
        """Return active patients with profiles"""
        return self.filter(
            role='patient', 
            is_active=True, 
            patient_profile__isnull=False, 
            patient_profile__is_active=True
        )
