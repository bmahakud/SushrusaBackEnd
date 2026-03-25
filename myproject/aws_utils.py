"""
Utility functions for safely accessing AWS settings
"""

from django.conf import settings

def get_aws_settings():
    """
    Safely get AWS settings, returning None for missing settings
    """
    aws_config = {}
    
    # Check if AWS settings are available
    if not hasattr(settings, 'ALWAYS_UPLOAD_FILES_TO_AWS') or not settings.ALWAYS_UPLOAD_FILES_TO_AWS:
        return None
    
    # Get AWS settings safely
    aws_config['access_key_id'] = getattr(settings, 'AWS_ACCESS_KEY_ID', None)
    aws_config['secret_access_key'] = getattr(settings, 'AWS_SECRET_ACCESS_KEY', None)
    aws_config['storage_bucket_name'] = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', None)
    aws_config['s3_endpoint_url'] = getattr(settings, 'AWS_S3_ENDPOINT_URL', None)
    aws_config['s3_region_name'] = getattr(settings, 'AWS_S3_REGION_NAME', None)
    aws_config['location'] = getattr(settings, 'AWS_LOCATION', None)
    
    # Check if all required settings are present
    required_settings = ['access_key_id', 'secret_access_key', 'storage_bucket_name', 
                        's3_endpoint_url', 's3_region_name', 'location']
    
    for setting in required_settings:
        if not aws_config[setting]:
            return None
    
    return aws_config

def is_aws_configured():
    """
    Check if AWS is properly configured
    """
    return get_aws_settings() is not None
