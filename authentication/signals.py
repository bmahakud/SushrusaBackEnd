"""
Signals for automatic file upload to DigitalOcean Spaces
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import User
import threading
import boto3
import os

def upload_profile_picture_async(user_id):
    """
    Asynchronous function to upload profile picture to DigitalOcean Spaces
    """
    try:
        from authentication.models import User
        
        # Get the user
        user = User.objects.get(id=user_id)
        
        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        # Upload profile picture if it exists
        if user.profile_picture and hasattr(user.profile_picture, 'path'):
            local_path = user.profile_picture.path
            if os.path.exists(local_path):
                remote_key = f"{settings.AWS_LOCATION}/{user.profile_picture.name}"
                try:
                    s3_client.upload_file(local_path, settings.AWS_STORAGE_BUCKET_NAME, remote_key)
                    # Make file public
                    s3_client.put_object_acl(
                        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                        Key=remote_key,
                        ACL='public-read'
                    )
                    print(f"✅ [ASYNC] Uploaded profile picture to DigitalOcean Spaces: {remote_key}")
                except Exception as e:
                    print(f"❌ [ASYNC] Error uploading profile picture: {e}")
                    
    except Exception as e:
        print(f"❌ [ASYNC] Error in upload_profile_picture_async: {e}")

def upload_profile_picture_sync(user_id):
    """
    Synchronous function to upload profile picture to DigitalOcean Spaces immediately
    """
    try:
        from authentication.models import User
        
        # Get the user
        user = User.objects.get(id=user_id)
        
        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        # Upload profile picture if it exists
        if user.profile_picture and hasattr(user.profile_picture, 'path'):
            local_path = user.profile_picture.path
            if os.path.exists(local_path):
                remote_key = f"{settings.AWS_LOCATION}/{user.profile_picture.name}"
                try:
                    s3_client.upload_file(local_path, settings.AWS_STORAGE_BUCKET_NAME, remote_key)
                    # Make file public
                    s3_client.put_object_acl(
                        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                        Key=remote_key,
                        ACL='public-read'
                    )
                    print(f"✅ [SYNC] Uploaded profile picture to DigitalOcean Spaces: {remote_key}")
                except Exception as e:
                    print(f"❌ [SYNC] Error uploading profile picture: {e}")
                    
    except Exception as e:
        print(f"❌ [SYNC] Error in upload_profile_picture_sync: {e}")

@receiver(post_save, sender=User)
def upload_user_profile_picture_to_spaces(sender, instance, created, **kwargs):
    """
    Automatically upload user profile picture to DigitalOcean Spaces after saving
    """
    if not settings.ALWAYS_UPLOAD_FILES_TO_AWS:
        return
    
    try:
        # For immediate access, upload synchronously first, then start async thread for any retries
        upload_profile_picture_sync(instance.id)
        
        # Also start async thread for any additional processing
        thread = threading.Thread(target=upload_profile_picture_async, args=(instance.id,))
        thread.daemon = True  # Thread will be killed when main process exits
        thread.start()
        print(f"🚀 [SIGNAL] Started async upload thread for user {instance.id}")
                    
    except Exception as e:
        print(f"❌ Error in upload_user_profile_picture_to_spaces signal: {e}") 