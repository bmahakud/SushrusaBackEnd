import random
import string
import hashlib
import hmac
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging
import requests

logger = logging.getLogger(__name__)


def generate_otp(length=6):
    """Generate a random OTP of specified length"""
    return ''.join(random.choices(string.digits, k=length))


def send_otp_via_msg91(phone, otp, template_id, authkey, otp_length=5, extra_params=None):
    """Send OTP via MSG91 API"""
    url = 'https://control.msg91.com/api/v5/otp'
    payload = {
        'template_id': template_id,
        'mobile': phone,
        'authkey': authkey,
        'otp': otp,
        'otp_length': otp_length
    }
    if extra_params:
        payload.update(extra_params)
    headers = {'Content-Type': 'application/JSON'}
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        logger.error(f"MSG91 OTP send failed for {phone}: {str(e)}")
        return False


def send_otp_sms(phone, otp, purpose='login'):
    """Send OTP via SMS using MSG91"""
    try:
        # Format message based on purpose (optional, MSG91 uses template)
        # Get MSG91 config from settings
        template_id = getattr(settings, 'MSG91_TEMPLATE_ID', None)
        authkey = getattr(settings, 'MSG91_AUTHKEY', None)
        otp_length = len(otp)
        if not template_id or not authkey:
            logger.error('MSG91 credentials not set in settings.')
            return False
        return send_otp_via_msg91(phone, otp, template_id, authkey, otp_length)
    except Exception as e:
        logger.error(f"Failed to send OTP via MSG91 to {phone}: {str(e)}")
        return False


def send_otp_via_twilio(phone, message):
    """Send OTP via Twilio"""
    try:
        from twilio.rest import Client
        
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        message = client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone
        )
        
        logger.info(f"Twilio SMS sent successfully. SID: {message.sid}")
        return True
        
    except Exception as e:
        logger.error(f"Twilio SMS failed: {str(e)}")
        return False


def send_otp_via_aws_sns(phone, message):
    """Send OTP via AWS SNS"""
    try:
        import boto3
        
        sns = boto3.client(
            'sns',
            region_name=settings.AWS_SNS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        
        response = sns.publish(
            PhoneNumber=phone,
            Message=message,
            MessageAttributes={
                'AWS.SNS.SMS.SMSType': {
                    'DataType': 'String',
                    'StringValue': 'Transactional'
                }
            }
        )
        
        logger.info(f"AWS SNS SMS sent successfully. MessageId: {response['MessageId']}")
        return True
        
    except Exception as e:
        logger.error(f"AWS SNS SMS failed: {str(e)}")
        return False


def send_otp_email(email, otp, purpose='login'):
    """Send OTP via email as backup"""
    try:
        subject = 'Sushrusa - Your OTP Code'
        
        # Prepare context for email template
        context = {
            'otp': otp,
            'purpose': purpose,
            'validity_minutes': 5
        }
        
        # Render email template
        html_message = render_to_string('authentication/otp_email.html', context)
        plain_message = strip_tags(html_message)
        
        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False
        )
        
        logger.info(f"OTP email sent successfully to {email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send OTP email to {email}: {str(e)}")
        return False


def format_phone_number(phone):
    """Format phone number to international format"""
    # Remove all non-digit characters
    phone = ''.join(filter(str.isdigit, phone))
    
    # Add country code if not present (assuming India +91)
    if not phone.startswith('91') and len(phone) == 10:
        phone = '91' + phone
    
    # Add + prefix
    if not phone.startswith('+'):
        phone = '+' + phone
    
    return phone


def validate_phone_number(phone):
    """Validate phone number format"""
    try:
        formatted_phone = format_phone_number(phone)
        
        # Basic validation for Indian phone numbers
        if formatted_phone.startswith('+91') and len(formatted_phone) == 13:
            return True, formatted_phone
        
        # Add validation for other countries as needed
        return False, "Invalid phone number format"
        
    except Exception:
        return False, "Invalid phone number format"


def generate_verification_code():
    """Generate a unique verification code for documents/accounts"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))


def create_digital_signature(data, secret_key=None):
    """Create digital signature for prescriptions/documents"""
    if secret_key is None:
        secret_key = settings.SECRET_KEY
    
    # Convert data to string if it's not already
    if not isinstance(data, str):
        data = str(data)
    
    # Create HMAC signature
    signature = hmac.new(
        secret_key.encode('utf-8'),
        data.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return signature


def verify_digital_signature(data, signature, secret_key=None):
    """Verify digital signature"""
    if secret_key is None:
        secret_key = settings.SECRET_KEY
    
    expected_signature = create_digital_signature(data, secret_key)
    return hmac.compare_digest(signature, expected_signature)


def get_user_role_permissions(role):
    """Get permissions based on user role"""
    permissions = {
        'patient': [
            'view_own_profile',
            'update_own_profile',
            'book_consultation',
            'view_own_consultations',
            'view_own_prescriptions',
            'make_payment',
            'submit_review'
        ],
        'doctor': [
            'view_own_profile',
            'update_own_profile',
            'view_assigned_consultations',
            'update_consultation_status',
            'create_prescription',
            'view_patient_medical_history',
            'manage_schedule'
        ],
        'admin': [
            'view_all_users',
            'manage_users',
            'view_all_consultations',
            'manage_consultations',
            'view_analytics',
            'manage_clinic_settings',
            'verify_documents'
        ],
        'superadmin': [
            'all_permissions'
        ]
    }
    
    return permissions.get(role, [])


def check_user_permission(user, permission):
    """Check if user has specific permission"""
    user_permissions = get_user_role_permissions(user.role)
    
    # Superadmin has all permissions
    if 'all_permissions' in user_permissions:
        return True
    
    return permission in user_permissions


class AuthenticationMiddleware:
    """Custom authentication middleware for additional security"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Add custom authentication logic here if needed
        response = self.get_response(request)
        return response
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        # Add request-level authentication checks
        pass

