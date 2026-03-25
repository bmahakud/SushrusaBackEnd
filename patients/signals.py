"""
Signals for automatic file upload to DigitalOcean Spaces
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import PatientProfile, PatientDocument, MedicalRecord
import threading
import boto3
import os

def upload_medical_record_async(record_id):
    """
    Asynchronous function to upload medical record to DigitalOcean Spaces
    """
    try:
        from patients.models import MedicalRecord
        
        # Get the medical record
        record = MedicalRecord.objects.get(id=record_id)
        
        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        # Upload document if it exists
        if record.document and hasattr(record.document, 'path'):
            local_path = record.document.path
            if os.path.exists(local_path):
                remote_key = f"{settings.AWS_LOCATION}/{record.document.name}"
                try:
                    s3_client.upload_file(local_path, settings.AWS_STORAGE_BUCKET_NAME, remote_key)
                    # Make file public
                    s3_client.put_object_acl(
                        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                        Key=remote_key,
                        ACL='public-read'
                    )
                    print(f"✅ [ASYNC] Uploaded medical record to DigitalOcean Spaces: {remote_key}")
                except Exception as e:
                    print(f"❌ [ASYNC] Error uploading medical record: {e}")
                    
    except Exception as e:
        print(f"❌ [ASYNC] Error in upload_medical_record_async: {e}")

def upload_medical_record_sync(record_id):
    """
    Synchronous function to upload medical record to DigitalOcean Spaces immediately
    """
    try:
        from patients.models import MedicalRecord
        
        # Get the medical record
        record = MedicalRecord.objects.get(id=record_id)
        
        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        # Upload document if it exists
        if record.document and hasattr(record.document, 'path'):
            local_path = record.document.path
            if os.path.exists(local_path):
                remote_key = f"{settings.AWS_LOCATION}/{record.document.name}"
                try:
                    s3_client.upload_file(local_path, settings.AWS_STORAGE_BUCKET_NAME, remote_key)
                    # Make file public
                    s3_client.put_object_acl(
                        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                        Key=remote_key,
                        ACL='public-read'
                    )
                    print(f"✅ [SYNC] Uploaded medical record to DigitalOcean Spaces: {remote_key}")
                except Exception as e:
                    print(f"❌ [SYNC] Error uploading medical record: {e}")
                    
    except Exception as e:
        print(f"❌ [SYNC] Error in upload_medical_record_sync: {e}")

def upload_patient_document_async(document_id):
    """
    Asynchronous function to upload patient document to DigitalOcean Spaces
    """
    try:
        from patients.models import PatientDocument
        
        # Get the document
        document = PatientDocument.objects.get(id=document_id)
        
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
                    print(f"✅ [ASYNC] Uploaded patient document to DigitalOcean Spaces: {remote_key}")
                except Exception as e:
                    print(f"❌ [ASYNC] Error uploading patient document: {e}")
                    
    except Exception as e:
        print(f"❌ [ASYNC] Error in upload_patient_document_async: {e}")

def upload_patient_document_sync(document_id):
    """
    Synchronous function to upload patient document to DigitalOcean Spaces immediately
    """
    try:
        from patients.models import PatientDocument
        
        # Get the document
        document = PatientDocument.objects.get(id=document_id)
        
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
                    print(f"✅ [SYNC] Uploaded patient document to DigitalOcean Spaces: {remote_key}")
                except Exception as e:
                    print(f"❌ [SYNC] Error uploading patient document: {e}")
                    
    except Exception as e:
        print(f"❌ [SYNC] Error in upload_patient_document_sync: {e}")

@receiver(post_save, sender=MedicalRecord)
def upload_medical_record_to_spaces(sender, instance, created, **kwargs):
    """
    Automatically upload medical record to DigitalOcean Spaces after saving
    """
    if not settings.ALWAYS_UPLOAD_FILES_TO_AWS:
        return
    
    try:
        # For immediate access, upload synchronously first, then start async thread for any retries
        upload_medical_record_sync(instance.id)
        
        # Also start async thread for any additional processing
        thread = threading.Thread(target=upload_medical_record_async, args=(instance.id,))
        thread.daemon = True  # Thread will be killed when main process exits
        thread.start()
        print(f"🚀 [SIGNAL] Started async upload thread for medical record {instance.id}")
                    
    except Exception as e:
        print(f"❌ Error in upload_medical_record_to_spaces signal: {e}")

@receiver(post_save, sender=PatientDocument)
def upload_patient_document_to_spaces(sender, instance, created, **kwargs):
    """
    Automatically upload patient document to DigitalOcean Spaces after saving
    """
    if not settings.ALWAYS_UPLOAD_FILES_TO_AWS:
        return
    
    try:
        # For immediate access, upload synchronously first, then start async thread for any retries
        upload_patient_document_sync(instance.id)
        
        # Also start async thread for any additional processing
        thread = threading.Thread(target=upload_patient_document_async, args=(instance.id,))
        thread.daemon = True  # Thread will be killed when main process exits
        thread.start()
        print(f"🚀 [SIGNAL] Started async upload thread for patient document {instance.id}")
                    
    except Exception as e:
        print(f"❌ Error in upload_patient_document_to_spaces signal: {e}") 