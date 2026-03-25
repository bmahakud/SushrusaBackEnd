from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import timedelta
import random
import string
import hashlib
from .models import User, OTP, UserSession
from django.conf import settings
from .utils import send_otp_sms


class SendOTPSerializer(serializers.Serializer):
    """Serializer for sending OTP"""
    phone = serializers.CharField(max_length=17)
    purpose = serializers.ChoiceField(choices=OTP._meta.get_field('purpose').choices, default='login')
    
    def validate_phone(self, value):
        """Validate phone number format"""
        # Remove spaces and special characters
        phone = ''.join(filter(str.isdigit, value))
        
        # Add country code if not present
        if not phone.startswith('91') and len(phone) == 10:
            phone = '91' + phone
        
        # Format with +
        if not phone.startswith('+'):
            phone = '+' + phone
        
        return phone
    
    def create(self, validated_data):
        """Create and send OTP"""
        phone = validated_data['phone']
        purpose = validated_data['purpose']

        # For login purpose, check if user exists
        if purpose == 'login':
            try:
                user = User.objects.get(phone=phone)
                if not user.is_active:
                    raise serializers.ValidationError('Account is deactivated. Please contact support.')
            except User.DoesNotExist:
                raise serializers.ValidationError('No account found with this phone number. Please register first.')

        # Check if test mode is enabled
        test_mode = getattr(settings, 'OTP_TEST_MODE', False)
        test_otp = getattr(settings, 'OTP_TEST_CODE', '999999')

        if test_mode:
            # In test mode, use the test OTP
            otp_code = test_otp
            # Hash the test OTP
            otp_hash = hashlib.sha256(otp_code.encode('utf-8')).hexdigest()
            
            # Set expiry time (5 minutes from now)
            expires_at = timezone.now() + timedelta(minutes=5)

            # Invalidate previous OTPs for this phone
            OTP.objects.filter(phone=phone, purpose=purpose, is_used=False).update(is_used=True)

            # Create new OTP (store hash)
            otp = OTP.objects.create(
                phone=phone,
                otp=otp_hash,
                purpose=purpose,
                expires_at=expires_at
            )

            return {
                'phone': phone,
                'expires_in': 300,
                'message': f'Test OTP sent successfully. Use {test_otp} for verification.',
                'test_otp': test_otp  # Include test OTP in response for convenience
            }
        else:
            # Production mode - generate random OTP
            otp_code = ''.join(random.choices(string.digits, k=6))
            # Hash the OTP
            otp_hash = hashlib.sha256(otp_code.encode('utf-8')).hexdigest()

            # Set expiry time (5 minutes from now)
            expires_at = timezone.now() + timedelta(minutes=5)

            # Invalidate previous OTPs for this phone
            OTP.objects.filter(phone=phone, purpose=purpose, is_used=False).update(is_used=True)

            # Create new OTP (store hash)
            otp = OTP.objects.create(
                phone=phone,
                otp=otp_hash,
                purpose=purpose,
                expires_at=expires_at
            )

            # Send OTP via SMS (production)
            send_otp_sms(phone, otp_code, purpose)

            return {
                'phone': phone,
                'expires_in': 300,
                'message': 'OTP sent successfully'
            }


class VerifyOTPSerializer(serializers.Serializer):
    """Serializer for verifying OTP and login/registration"""
    phone = serializers.CharField(max_length=17)
    otp = serializers.CharField(max_length=6)
    purpose = serializers.ChoiceField(choices=OTP._meta.get_field('purpose').choices, default='login')
    user_info = serializers.DictField(required=False)
    
    def validate_phone(self, value):
        """Validate phone number format"""
        # Remove spaces and special characters
        phone = ''.join(filter(str.isdigit, value))
        
        # Add country code if not present
        if not phone.startswith('91') and len(phone) == 10:
            phone = '91' + phone
        
        # Format with +
        if not phone.startswith('+'):
            phone = '+' + phone
        
        return phone
    
    def validate(self, attrs):
        """Validate OTP and return user"""
        phone = attrs['phone']
        otp_code = attrs['otp']
        purpose = attrs.get('purpose', 'login')
        user_info = attrs.get('user_info', {})

        # Check if test mode is enabled
        test_mode = getattr(settings, 'OTP_TEST_MODE', False)
        test_otp = getattr(settings, 'OTP_TEST_CODE', '999999')

        # Handle test OTP bypass
        if test_mode and otp_code == test_otp:
            try:
                user = User.objects.get(phone=phone)
                if not user.is_active:
                    raise serializers.ValidationError('Account is deactivated. Please contact support.')
                attrs['user'] = user
                attrs['is_new_user'] = False
            except User.DoesNotExist:
                if purpose == 'registration':
                    # Create new user for registration
                    if not user_info.get('name'):
                        raise serializers.ValidationError('Name is required for registration')
                    
                    user = User.objects.create_user(
                        phone=phone,
                        name=user_info['name'],
                        role=user_info.get('role', 'patient'),
                        date_of_birth=user_info.get('date_of_birth')
                    )
                    attrs['user'] = user
                    attrs['is_new_user'] = True
                else:
                    raise serializers.ValidationError('No account found with this phone number. Please register first.')
            return attrs

        # Hash the provided OTP
        otp_hash = hashlib.sha256(otp_code.encode('utf-8')).hexdigest()

        # Find valid OTP (by hash and purpose)
        try:
            otp = OTP.objects.get(
                phone=phone,
                otp=otp_hash,
                purpose=purpose,
                is_used=False,
                expires_at__gt=timezone.now()
            )
        except OTP.DoesNotExist:
            raise serializers.ValidationError('Invalid or expired OTP')

        # Mark OTP as used
        otp.is_used = True
        otp.save()

        # Handle user creation/retrieval based on purpose
        try:
            user = User.objects.get(phone=phone)
            if not user.is_active:
                raise serializers.ValidationError('Account is deactivated. Please contact support.')
            attrs['user'] = user
            attrs['is_new_user'] = False
        except User.DoesNotExist:
            if purpose == 'registration':
                # Create new user for registration
                if not user_info.get('name'):
                    raise serializers.ValidationError('Name is required for registration')
                
                user = User.objects.create_user(
                    phone=phone,
                    name=user_info['name'],
                    role=user_info.get('role', 'patient'),
                    date_of_birth=user_info.get('date_of_birth')
                )
                attrs['user'] = user
                attrs['is_new_user'] = True
            else:
                raise serializers.ValidationError('No account found with this phone number. Please register first.')

        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""
    age = serializers.ReadOnlyField()
    full_address = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = [
            'id', 'phone', 'email', 'name', 'role', 'date_of_birth', 'gender',
            'profile_picture', 'street', 'city', 'state', 'pincode', 'country',
            'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship',
            'blood_group', 'allergies', 'medical_history', 'is_verified', 'date_joined',
            'age', 'full_address'
        ]
        read_only_fields = ['id', 'phone', 'role', 'is_verified', 'date_joined']


class UpdateProfileSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile"""
    
    class Meta:
        model = User
        fields = [
            'name', 'phone', 'email', 'date_of_birth', 'gender', 'profile_picture',
            'street', 'city', 'state', 'pincode', 'country',
            'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship',
            'blood_group', 'allergies', 'medical_history'
        ]
    
    def validate_email(self, value):
        """Validate email uniqueness"""
        if value:
            # Only validate if email is actually being changed
            if self.instance and self.instance.email == value:
                # Email hasn't changed, no need to validate uniqueness
                return value
                
            # Check if email exists for other users
            existing_user = User.objects.filter(email=value).exclude(id=self.instance.id if self.instance else None).first()
            if existing_user:
                raise serializers.ValidationError(f'Email already exists for user: {existing_user.name} (ID: {existing_user.id})')
        return value


class AdminUpdateUserSerializer(serializers.ModelSerializer):
    """Serializer for admin/superadmin updating any user profile including phone"""
    
    class Meta:
        model = User
        fields = [
            'name', 'email', 'phone', 'date_of_birth', 'gender', 'profile_picture',
            'street', 'city', 'state', 'pincode', 'country',
            'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship',
            'blood_group', 'allergies', 'medical_history'
        ]
    
    def validate_email(self, value):
        """Validate email uniqueness"""
        if value:
            # Only validate if email is actually being changed
            if self.instance and self.instance.email == value:
                # Email hasn't changed, no need to validate uniqueness
                return value
                
            # Check if email exists for other users
            existing_user = User.objects.filter(email=value).exclude(id=self.instance.id if self.instance else None).first()
            if existing_user:
                raise serializers.ValidationError(f'Email already exists for user: {existing_user.name} (ID: {existing_user.id})')
        return value
    
    def validate_phone(self, value):
        """Validate phone uniqueness"""
        if value:
            # Check if phone exists for other users
            existing_user = User.objects.filter(phone=value).exclude(id=self.instance.id).first()
            if existing_user:
                raise serializers.ValidationError(f'Phone number already exists for user: {existing_user.name} (ID: {existing_user.id})')
        return value


class RefreshTokenSerializer(serializers.Serializer):
    """Serializer for refreshing JWT token"""
    refresh = serializers.CharField()
    
    def validate_refresh(self, value):
        """Validate refresh token"""
        try:
            from rest_framework_simplejwt.tokens import RefreshToken
            token = RefreshToken(value)
            return token
        except Exception:
            raise serializers.ValidationError('Invalid refresh token')


class LogoutSerializer(serializers.Serializer):
    """Serializer for logout"""
    refresh = serializers.CharField()
    
    def validate_refresh(self, value):
        """Validate refresh token"""
        try:
            from rest_framework_simplejwt.tokens import RefreshToken
            token = RefreshToken(value)
            return token
        except Exception:
            raise serializers.ValidationError('Invalid refresh token')
    
    def save(self):
        """Blacklist the refresh token"""
        try:
            token = self.validated_data['refresh']
            token.blacklist()
        except Exception:
            pass


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password"""
    old_password = serializers.CharField()
    new_password = serializers.CharField(min_length=8)
    confirm_password = serializers.CharField()
    
    def validate(self, attrs):
        """Validate password change"""
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError('New passwords do not match')
        return attrs
    
    def validate_old_password(self, value):
        """Validate old password"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Invalid old password')
        return value


class UserSessionSerializer(serializers.ModelSerializer):
    """Serializer for user sessions"""
    
    class Meta:
        model = UserSession
        fields = ['device_info', 'ip_address', 'is_active', 'created_at', 'last_used']
        read_only_fields = ['created_at', 'last_used']

