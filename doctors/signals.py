"""
Signals for automatic file upload to DigitalOcean Spaces
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.utils import timezone
from .models import DoctorProfile, DoctorDocument, DoctorEducation, DoctorStatus
import threading
import boto3
import os
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from authentication.models import User
from .models import DoctorStatus, DoctorProfile
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json


def upload_doctor_education_async(education_id):
    """
    Asynchronous function to upload doctor education certificate to DigitalOcean Spaces
    """
    try:
        from doctors.models import DoctorEducation
        
        # Get the education
        education = DoctorEducation.objects.get(id=education_id)
        
        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        # Upload certificate if it exists
        if education.certificate and hasattr(education.certificate, 'path'):
            local_path = education.certificate.path
            if os.path.exists(local_path):
                remote_key = f"{settings.AWS_LOCATION}/{education.certificate.name}"
                try:
                    s3_client.upload_file(local_path, settings.AWS_STORAGE_BUCKET_NAME, remote_key)
                    # Make file public
                    s3_client.put_object_acl(
                        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                        Key=remote_key,
                        ACL='public-read'
                    )
                    print(f"✅ [ASYNC] Uploaded doctor education certificate to DigitalOcean Spaces: {remote_key}")
                except Exception as e:
                    print(f"❌ [ASYNC] Error uploading doctor education certificate: {e}")
                    
    except Exception as e:
        print(f"❌ [ASYNC] Error in upload_doctor_education_async: {e}")

def upload_doctor_education_sync(education_id):
    """
    Synchronous function to upload doctor education certificate to DigitalOcean Spaces immediately
    """
    try:
        from doctors.models import DoctorEducation
        
        # Get the education
        education = DoctorEducation.objects.get(id=education_id)
        
        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        # Upload certificate if it exists
        if education.certificate and hasattr(education.certificate, 'path'):
            local_path = education.certificate.path
            if os.path.exists(local_path):
                remote_key = f"{settings.AWS_LOCATION}/{education.certificate.name}"
                try:
                    s3_client.upload_file(local_path, settings.AWS_STORAGE_BUCKET_NAME, remote_key)
                    # Make file public
                    s3_client.put_object_acl(
                        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                        Key=remote_key,
                        ACL='public-read'
                    )
                    print(f"✅ [SYNC] Uploaded doctor education certificate to DigitalOcean Spaces: {remote_key}")
                except Exception as e:
                    print(f"❌ [SYNC] Error uploading doctor education certificate: {e}")
                    
    except Exception as e:
        print(f"❌ [SYNC] Error in upload_doctor_education_sync: {e}")

def upload_doctor_document_async(document_id):
    """
    Asynchronous function to upload doctor document to DigitalOcean Spaces
    """
    try:
        from doctors.models import DoctorDocument
        
        # Get the document
        document = DoctorDocument.objects.get(id=document_id)
        
        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        # Upload document if it exists
        if document.file and hasattr(document.file, 'path'):
            local_path = document.file.path
            if os.path.exists(local_path):
                remote_key = f"{settings.AWS_LOCATION}/{document.file.name}"
                try:
                    s3_client.upload_file(local_path, settings.AWS_STORAGE_BUCKET_NAME, remote_key)
                    # Make file public
                    s3_client.put_object_acl(
                        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                        Key=remote_key,
                        ACL='public-read'
                    )
                    print(f"✅ [ASYNC] Uploaded doctor document to DigitalOcean Spaces: {remote_key}")
                except Exception as e:
                    print(f"❌ [ASYNC] Error uploading doctor document: {e}")
                    
    except Exception as e:
        print(f"❌ [ASYNC] Error in upload_doctor_document_async: {e}")

def upload_doctor_document_sync(document_id):
    """
    Synchronous function to upload doctor document to DigitalOcean Spaces immediately
    """
    try:
        from doctors.models import DoctorDocument
        
        # Get the document
        document = DoctorDocument.objects.get(id=document_id)
        
        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        # Upload document if it exists
        if document.file and hasattr(document.file, 'path'):
            local_path = document.file.path
            if os.path.exists(local_path):
                remote_key = f"{settings.AWS_LOCATION}/{document.file.name}"
                try:
                    s3_client.upload_file(local_path, settings.AWS_STORAGE_BUCKET_NAME, remote_key)
                    # Make file public
                    s3_client.put_object_acl(
                        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                        Key=remote_key,
                        ACL='public-read'
                    )
                    print(f"✅ [SYNC] Uploaded doctor document to DigitalOcean Spaces: {remote_key}")
                except Exception as e:
                    print(f"❌ [SYNC] Error uploading doctor document: {e}")
                    
    except Exception as e:
        print(f"❌ [SYNC] Error in upload_doctor_document_sync: {e}")

def upload_doctor_signature_async(profile_id):
    """
    Asynchronous function to upload doctor signature to DigitalOcean Spaces
    """
    try:
        from doctors.models import DoctorProfile
        
        # Get the profile
        profile = DoctorProfile.objects.get(id=profile_id)
        
        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        # Upload signature if it exists
        if profile.signature:
            # Try to get the path - handle both FileField and string paths
            try:
                local_path = profile.signature.path
            except Exception:
                # If path fails, construct it from MEDIA_ROOT and signature name
                local_path = os.path.join(settings.MEDIA_ROOT, str(profile.signature))
            
            signature_name = str(profile.signature)
            
            if os.path.exists(local_path):
                remote_key = f"{settings.AWS_LOCATION}/{signature_name}"
                try:
                    s3_client.upload_file(local_path, settings.AWS_STORAGE_BUCKET_NAME, remote_key)
                    # Make file public
                    s3_client.put_object_acl(
                        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                        Key=remote_key,
                        ACL='public-read'
                    )
                    print(f"✅ [ASYNC] Uploaded doctor signature to DigitalOcean Spaces: {remote_key}")
                except Exception as e:
                    print(f"❌ [ASYNC] Error uploading doctor signature: {e}")
                    
    except Exception as e:
        print(f"❌ [ASYNC] Error in upload_doctor_signature_async: {e}")

def upload_doctor_signature_sync(profile_id):
    """
    Synchronous function to upload doctor signature to DigitalOcean Spaces immediately
    """
    try:
        from doctors.models import DoctorProfile
        
        # Get the profile
        profile = DoctorProfile.objects.get(id=profile_id)
        
        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        # Upload signature if it exists
        if profile.signature:
            # Try to get the path - handle both FileField and string paths
            try:
                local_path = profile.signature.path
            except Exception:
                # If path fails, construct it from MEDIA_ROOT and signature name
                local_path = os.path.join(settings.MEDIA_ROOT, str(profile.signature))
            
            signature_name = str(profile.signature)
            
            if os.path.exists(local_path):
                remote_key = f"{settings.AWS_LOCATION}/{signature_name}"
                try:
                    s3_client.upload_file(local_path, settings.AWS_STORAGE_BUCKET_NAME, remote_key)
                    # Make file public
                    s3_client.put_object_acl(
                        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                        Key=remote_key,
                        ACL='public-read'
                    )
                    print(f"✅ [SYNC] Uploaded doctor signature to DigitalOcean Spaces: {remote_key}")
                except Exception as e:
                    print(f"❌ [SYNC] Error uploading doctor signature: {e}")
                    
    except Exception as e:
        print(f"❌ [SYNC] Error in upload_doctor_signature_sync: {e}")

@receiver(post_save, sender=DoctorEducation)
def upload_doctor_education_to_spaces(sender, instance, created, **kwargs):
    """
    Automatically upload doctor education certificate to DigitalOcean Spaces after saving
    """
    if not settings.ALWAYS_UPLOAD_FILES_TO_AWS:
        return
    
    try:
        # For immediate access, upload synchronously first, then start async thread for any retries
        upload_doctor_education_sync(instance.id)
        
        # Also start async thread for any additional processing
        thread = threading.Thread(target=upload_doctor_education_async, args=(instance.id,))
        thread.daemon = True  # Thread will be killed when main process exits
        thread.start()
        print(f"🚀 [SIGNAL] Started async upload thread for doctor education {instance.id}")
                    
    except Exception as e:
        print(f"❌ Error in upload_doctor_education_to_spaces signal: {e}")

@receiver(post_save, sender=DoctorDocument)
def upload_doctor_document_to_spaces(sender, instance, created, **kwargs):
    """
    Automatically upload doctor document to DigitalOcean Spaces after saving
    """
    if not settings.ALWAYS_UPLOAD_FILES_TO_AWS:
        return
    
    try:
        # For immediate access, upload synchronously first, then start async thread for any retries
        upload_doctor_document_sync(instance.id)
        
        # Also start async thread for any additional processing
        thread = threading.Thread(target=upload_doctor_document_async, args=(instance.id,))
        thread.daemon = True  # Thread will be killed when main process exits
        thread.start()
        print(f"🚀 [SIGNAL] Started async upload thread for doctor document {instance.id}")
                    
    except Exception as e:
        print(f"❌ Error in upload_doctor_document_to_spaces signal: {e}") 

@receiver(post_save, sender=DoctorProfile)
def upload_doctor_signature_to_spaces(sender, instance, created, **kwargs):
    """
    Automatically upload doctor signature to DigitalOcean Spaces after saving DoctorProfile
    """
    if not settings.ALWAYS_UPLOAD_FILES_TO_AWS:
        return
    
    # Only upload if signature field was updated
    if instance.signature:
        try:
            # For immediate access, upload synchronously first, then start async thread for any retries
            upload_doctor_signature_sync(instance.id)
            
            # Also start async thread for any additional processing
            thread = threading.Thread(target=upload_doctor_signature_async, args=(instance.id,))
            thread.daemon = True  # Thread will be killed when main process exits
            thread.start()
            print(f"🚀 [SIGNAL] Started async upload thread for doctor signature {instance.id}")
                        
        except Exception as e:
            print(f"❌ Error in upload_doctor_signature_to_spaces signal: {e}")

@receiver(post_save, sender=DoctorProfile)
def create_doctor_status(sender, instance, created, **kwargs):
    """Create DoctorStatus record when a new DoctorProfile is created"""
    if created:
        DoctorStatus.objects.create(
            doctor=instance,
            is_online=False,
            is_logged_in=False,
            is_available=True,
            current_status='offline',
            last_activity=timezone.now(),
            status_updated_at=timezone.now(),
            status_note='',
            auto_away_threshold=15,
        )

@receiver(post_save, sender=User)
def update_doctor_status_on_login(sender, instance, created, **kwargs):
    """
    Update doctor status when user logs in (last_login is updated)
    """
    if not created and instance.role == 'doctor':
        try:
            # Check if this is a login event (last_login was updated)
            if hasattr(instance, '_state') and instance._state.fields_cache.get('last_login'):
                doctor_profile = DoctorProfile.objects.get(user=instance)
                doctor_status, created = DoctorStatus.objects.get_or_create(
                    doctor=doctor_profile,
                    defaults={
                        'is_online': True,
                        'is_logged_in': True,
                        'is_available': True,
                        'current_status': 'available',
                        'last_login': timezone.now(),
                        'last_activity': timezone.now(),
                    }
                )
                
                if not created:
                    # Update existing status
                    doctor_status.is_online = True
                    doctor_status.is_logged_in = True
                    doctor_status.is_available = True
                    doctor_status.current_status = 'available'
                    doctor_status.last_login = timezone.now()
                    doctor_status.last_activity = timezone.now()
                    doctor_status.save()
                
                # Broadcast status update via WebSocket
                broadcast_doctor_status_update(doctor_status)
                
        except DoctorProfile.DoesNotExist:
            # Doctor profile doesn't exist yet, skip
            pass


def mark_doctor_offline_if_inactive():
    """
    Mark doctors as offline if they haven't been active for more than 5 minutes
    This function can be called by a periodic task or cron job
    """
    from datetime import timedelta
    inactive_threshold = timezone.now() - timedelta(minutes=5)
    
    inactive_doctors = DoctorStatus.objects.filter(
        is_online=True,
        last_activity__lt=inactive_threshold
    )
    
    for doctor_status in inactive_doctors:
        doctor_status.is_online = False
        doctor_status.is_logged_in = False
        doctor_status.current_status = 'offline'
        doctor_status.save()
        
        # Broadcast the status change
        broadcast_doctor_status_update(doctor_status)
        
        print(f"Marked {doctor_status.doctor.user.name} as offline due to inactivity")


def broadcast_doctor_status_update(doctor_status):
    """
    Broadcast doctor status update to all connected clients via WebSocket
    """
    try:
        channel_layer = get_channel_layer()
        
        # Prepare status data
        status_data = {
            'doctor_id': doctor_status.doctor.id,
            'doctor_name': doctor_status.doctor.user.name,
            'doctor_email': doctor_status.doctor.user.email,
            'doctor_specialization': doctor_status.doctor.specialization,
            'doctor_profile_picture': doctor_status.doctor.user.profile_picture.url if doctor_status.doctor.user.profile_picture else None,
            'is_online': doctor_status.is_online,
            'is_logged_in': doctor_status.is_logged_in,
            'is_available': doctor_status.is_available,
            'current_status': doctor_status.current_status,
            'status_display': doctor_status.status_display,
            'is_active': doctor_status.is_active,
            'last_activity': doctor_status.last_activity.isoformat(),
            'last_activity_formatted': doctor_status.last_activity.strftime('%H:%M'),
            'last_login': doctor_status.last_login.isoformat() if doctor_status.last_login else None,
            'last_login_formatted': doctor_status.last_login.strftime('%H:%M') if doctor_status.last_login else None,
            'current_consultation': doctor_status.current_consultation.id if doctor_status.current_consultation else None,
            'current_consultation_info': {
                'id': doctor_status.current_consultation.id,
                'patient_name': doctor_status.current_consultation.patient.user.name,
                'scheduled_time': doctor_status.current_consultation.scheduled_time,
            } if doctor_status.current_consultation else None,
            'status_updated_at': doctor_status.status_updated_at.isoformat(),
            'status_note': doctor_status.status_note,
            'auto_away_threshold': doctor_status.auto_away_threshold,
        }
        
        # Send to doctor status group
        async_to_sync(channel_layer.group_send)(
            "doctor_status_updates",
            {
                'type': 'status_update',
                'data': status_data
            }
        )
        
    except Exception as e:
        # Log error but don't fail the signal
        print(f"Error broadcasting doctor status update: {e}")


@receiver(post_save, sender=DoctorStatus)
def broadcast_status_change(sender, instance, created, **kwargs):
    """
    Broadcast status changes to WebSocket clients
    """
    broadcast_doctor_status_update(instance) 