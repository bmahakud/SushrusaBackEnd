"""
Signals for automatic PDF upload to DigitalOcean Spaces
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import PrescriptionPDF, PrescriptionImage
import threading
import boto3
import os

def upload_pdf_async(pdf_id):
    """
    Asynchronous function to upload PDF to DigitalOcean Spaces
    """
    try:
        from prescriptions.models import PrescriptionPDF
        
        # Get the PDF instance
        pdf_instance = PrescriptionPDF.objects.get(id=pdf_id)
        
        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        # Upload PDF file if it exists
        if pdf_instance.pdf_file and hasattr(pdf_instance.pdf_file, 'path'):
            local_path = pdf_instance.pdf_file.path
            if os.path.exists(local_path):
                remote_key = f"{settings.AWS_LOCATION}/{pdf_instance.pdf_file.name}"
                try:
                    # Upload with correct Content-Type and Content-Disposition headers
                    with open(local_path, 'rb') as file_obj:
                        s3_client.upload_fileobj(
                            file_obj,
                            settings.AWS_STORAGE_BUCKET_NAME,
                            remote_key,
                            ExtraArgs={
                                'ContentType': 'application/pdf',
                                'ContentDisposition': 'inline',
                                'ACL': 'public-read'
                            }
                        )
                    print(f"✅ [ASYNC] Uploaded PDF to DigitalOcean Spaces: {remote_key}")
                except Exception as e:
                    print(f"❌ [ASYNC] Error uploading PDF: {e}")
                    
    except Exception as e:
        print(f"❌ [ASYNC] Error in upload_pdf_async: {e}")

def upload_pdf_sync(pdf_id):
    """
    Synchronous function to upload PDF to DigitalOcean Spaces immediately
    """
    try:
        from prescriptions.models import PrescriptionPDF
        
        # Get the PDF instance
        pdf_instance = PrescriptionPDF.objects.get(id=pdf_id)
        
        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        # Upload PDF file if it exists
        if pdf_instance.pdf_file and hasattr(pdf_instance.pdf_file, 'path'):
            local_path = pdf_instance.pdf_file.path
            if os.path.exists(local_path):
                remote_key = f"{settings.AWS_LOCATION}/{pdf_instance.pdf_file.name}"
                try:
                    # Upload with correct Content-Type and Content-Disposition headers
                    with open(local_path, 'rb') as file_obj:
                        s3_client.upload_fileobj(
                            file_obj,
                            settings.AWS_STORAGE_BUCKET_NAME,
                            remote_key,
                            ExtraArgs={
                                'ContentType': 'application/pdf',
                                'ContentDisposition': 'inline',
                                'ACL': 'public-read'
                            }
                        )
                    print(f"✅ [SYNC] Uploaded PDF to DigitalOcean Spaces: {remote_key}")
                except Exception as e:
                    print(f"❌ [SYNC] Error uploading PDF: {e}")
                    
    except Exception as e:
        print(f"❌ [SYNC] Error in upload_pdf_sync: {e}")

@receiver(post_save, sender=PrescriptionPDF)
def upload_prescription_pdf_to_spaces(sender, instance, created, **kwargs):
    """
    Automatically upload prescription PDF to DigitalOcean Spaces after saving
    """
    if not settings.ALWAYS_UPLOAD_FILES_TO_AWS:
        return
    
    try:
        # For immediate access, upload synchronously first, then start async thread for any retries
        upload_pdf_sync(instance.id)
        
        # Also start async thread for any additional processing
        thread = threading.Thread(target=upload_pdf_async, args=(instance.id,))
        thread.daemon = True  # Thread will be killed when main process exits
        thread.start()
        print(f"🚀 [SIGNAL] Started async upload thread for PDF {instance.id}")
                    
    except Exception as e:
        print(f"❌ Error in upload_prescription_pdf_to_spaces signal: {e}")


def upload_image_async(image_id):
    """
    Asynchronous function to upload prescription image to DigitalOcean Spaces
    """
    try:
        # Get the image instance
        image_instance = PrescriptionImage.objects.get(id=image_id)
        
        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        # Upload image file if it exists
        if image_instance.image_file and hasattr(image_instance.image_file, 'path'):
            local_path = image_instance.image_file.path
            if os.path.exists(local_path):
                remote_key = f"{settings.AWS_LOCATION}/{image_instance.image_file.name}"
                try:
                    # Upload with correct Content-Type headers
                    with open(local_path, 'rb') as file_obj:
                        s3_client.upload_fileobj(
                            file_obj,
                            settings.AWS_STORAGE_BUCKET_NAME,
                            remote_key,
                            ExtraArgs={
                                'ContentType': 'image/jpeg',  # Adjust based on actual image type
                                'ContentDisposition': 'inline',
                                'ACL': 'public-read'
                            }
                        )
                    print(f"✅ [ASYNC] Uploaded prescription image to DigitalOcean Spaces: {remote_key}")
                except Exception as e:
                    print(f"❌ [ASYNC] Error uploading prescription image: {e}")
                    
    except Exception as e:
        print(f"❌ [ASYNC] Error in upload_image_async: {e}")

def upload_image_sync(image_id):
    """
    Synchronous function to upload prescription image to DigitalOcean Spaces immediately
    """
    try:
        # Get the image instance
        image_instance = PrescriptionImage.objects.get(id=image_id)
        
        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        # Upload image file if it exists
        if image_instance.image_file and hasattr(image_instance.image_file, 'path'):
            local_path = image_instance.image_file.path
            if os.path.exists(local_path):
                remote_key = f"{settings.AWS_LOCATION}/{image_instance.image_file.name}"
                try:
                    # Upload with correct Content-Type headers
                    with open(local_path, 'rb') as file_obj:
                        s3_client.upload_fileobj(
                            file_obj,
                            settings.AWS_STORAGE_BUCKET_NAME,
                            remote_key,
                            ExtraArgs={
                                'ContentType': 'image/jpeg',  # Adjust based on actual image type
                                'ContentDisposition': 'inline',
                                'ACL': 'public-read'
                            }
                        )
                    print(f"✅ [SYNC] Uploaded prescription image to DigitalOcean Spaces: {remote_key}")
                except Exception as e:
                    print(f"❌ [SYNC] Error uploading prescription image: {e}")
                    
    except Exception as e:
        print(f"❌ [SYNC] Error in upload_image_sync: {e}")

@receiver(post_save, sender=PrescriptionImage)
def upload_prescription_image_to_spaces(sender, instance, created, **kwargs):
    """
    Automatically upload prescription image to DigitalOcean Spaces after saving
    """
    if not settings.ALWAYS_UPLOAD_FILES_TO_AWS:
        return
    
    try:
        # For immediate access, upload synchronously first, then start async thread for any retries
        upload_image_sync(instance.id)
        
        # Also start async thread for any additional processing
        thread = threading.Thread(target=upload_image_async, args=(instance.id,))
        thread.daemon = True  # Thread will be killed when main process exits
        thread.start()
        print(f"🚀 [SIGNAL] Started async upload thread for prescription image {instance.id}")
                    
    except Exception as e:
        print(f"❌ Error in upload_prescription_image_to_spaces signal: {e}") 