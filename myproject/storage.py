"""
Custom storage configuration for DigitalOcean Spaces
"""

from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings

class MediaStorage(S3Boto3Storage):
    """Custom storage for media files"""
    file_overwrite = False
    default_acl = 'public-read'
    bucket_name = 'edrspace'
    endpoint_url = 'https://sgp1.digitaloceanspaces.com'
    region_name = 'sgp1'
    location = 'edrcontainer1'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Force S3 storage configuration
        self.bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        self.endpoint_url = settings.AWS_S3_ENDPOINT_URL
        self.region_name = settings.AWS_S3_REGION_NAME
        self.location = getattr(settings, 'AWS_LOCATION', 'edrcontainer1')

class StaticStorage(S3Boto3Storage):
    """Custom storage for static files"""
    file_overwrite = True
    default_acl = 'public-read'
    bucket_name = 'edrspace'
    endpoint_url = 'https://sgp1.digitaloceanspaces.com'
    region_name = 'sgp1'
    location = 'edrcontainer1/static'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Force S3 storage configuration
        self.bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        self.endpoint_url = settings.AWS_S3_ENDPOINT_URL
        self.region_name = settings.AWS_S3_REGION_NAME
        self.location = f"{getattr(settings, 'AWS_LOCATION', 'edrcontainer1')}/static" 