"""
Utility functions for generating signed URLs for DigitalOcean Spaces
"""

import boto3
from botocore.config import Config
from django.conf import settings
import os

def generate_signed_url(file_key, expiration=3600):
    """
    Generate a signed URL for accessing a file in DigitalOcean Spaces
    Matches the format used in the other web app
    
    Args:
        file_key (str): The key/path of the file in the bucket
        expiration (int): URL expiration time in seconds (default: 1 hour)
    
    Returns:
        str: Signed URL for accessing the file
    """
    try:
        # Ensure file_key includes AWS_LOCATION prefix
        aws_location = getattr(settings, 'AWS_LOCATION', 'edrcontainer1')
        if not file_key.startswith(f"{aws_location}/"):
            file_key = f"{aws_location}/{file_key}"
        
        # Initialize S3 client for DigitalOcean Spaces
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        # Generate signed URL with the format used in the other app
        signed_url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                'Key': file_key
            },
            ExpiresIn=expiration
        )
        
        return signed_url
        
    except Exception as e:
        print(f"Error generating signed URL for {file_key}: {e}")
        # Fallback to public URL if signed URL generation fails
        return f"https://{settings.AWS_STORAGE_BUCKET_NAME}.sgp1.digitaloceanspaces.com/{file_key}"

def get_signed_media_url(file_path):
    """
    Generate signed URL for media files (uploads)
    
    Args:
        file_path (str): Full URL or relative path of the file
    
    Returns:
        str: Signed URL for the media file
    """
    if not file_path:
        return None
    
    # If it's a full DigitalOcean Spaces URL, extract the file key
    if file_path.startswith('https://'):
        # Extract the path after the domain and bucket
        # URL format: https://bucket.region.digitaloceanspaces.com/container/path/to/file
        try:
            from urllib.parse import urlparse
            parsed_url = urlparse(file_path)
            # Remove the leading slash and get the path
            file_key = parsed_url.path.lstrip('/')
            return generate_signed_url(file_key)
        except Exception as e:
            print(f"Error parsing URL {file_path}: {e}")
            return file_path  # Fallback to original URL
    
    # If it's a relative path, ensure it includes the container prefix
    aws_location = getattr(settings, 'AWS_LOCATION', 'edrcontainer1')
    if not file_path.startswith(f"{aws_location}/"):
        file_key = f"{aws_location}/{file_path}"
    else:
        file_key = file_path
    
    return generate_signed_url(file_key)

def get_signed_static_url(file_path):
    """
    Generate signed URL for static files
    
    Args:
        file_path (str): Full URL or relative path of the static file
    
    Returns:
        str: Signed URL for the static file
    """
    if not file_path:
        return None
    
    # If it's a full DigitalOcean Spaces URL, extract the file key
    if file_path.startswith('https://'):
        # Extract the path after the domain and bucket
        # URL format: https://bucket.region.digitaloceanspaces.com/container/path/to/file
        try:
            from urllib.parse import urlparse
            parsed_url = urlparse(file_path)
            # Remove the leading slash and get the path
            file_key = parsed_url.path.lstrip('/')
            return generate_signed_url(file_key)
        except Exception as e:
            print(f"Error parsing URL {file_path}: {e}")
            return file_path  # Fallback to original URL
    
    # If it's a relative path, ensure it includes the container prefix
    aws_location = getattr(settings, 'AWS_LOCATION', 'edrcontainer1')
    if not file_path.startswith(f"{aws_location}/"):
        file_key = f"{aws_location}/{file_path}"
    else:
        file_key = file_path
    
    return generate_signed_url(file_key)

def is_signed_url(url):
    """
    Check if a URL is a signed URL (contains AWS parameters)
    
    Args:
        url (str): URL to check
    
    Returns:
        bool: True if it's a signed URL, False otherwise
    """
    # Check for both old and new AWS SDK signed URL formats
    old_format = 'AWSAccessKeyId=' in url and 'Signature=' in url and 'Expires=' in url
    new_format = 'X-Amz-Algorithm=' in url and 'X-Amz-Signature=' in url and 'X-Amz-Date=' in url
    return old_format or new_format 