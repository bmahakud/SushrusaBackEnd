from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import OTP, UserSession
from .utils import generate_otp, send_otp

User = get_user_model()


class UserModelTest(TestCase):
    """Test cases for User model"""
    
    def setUp(self):
        self.user_data = {
            'phone': '+1234567890',
            'name': 'Test User',
            'email': 'test@example.com',
            'role': 'patient'
        }
    
    def test_create_user(self):
        """Test user creation"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.phone, self.user_data['phone'])
        self.assertEqual(user.name, self.user_data['name'])
        self.assertEqual(user.role, self.user_data['role'])
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
    
    def test_create_superuser(self):
        """Test superuser creation"""
        user = User.objects.create_superuser(
            phone='+1234567890',
            name='Admin User',
            password='testpass123'
        )
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertEqual(user.role, 'superadmin')
    
    def test_user_string_representation(self):
        """Test user string representation"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), f"{user.name} ({user.phone})")


class OTPModelTest(TestCase):
    """Test cases for OTP model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            phone='+1234567890',
            name='Test User',
            role='patient'
        )
    
    def test_create_otp(self):
        """Test OTP creation"""
        otp = OTP.objects.create(
            user=self.user,
            otp_code='123456',
            purpose='login'
        )
        self.assertEqual(otp.user, self.user)
        self.assertEqual(otp.otp_code, '123456')
        self.assertEqual(otp.purpose, 'login')
        self.assertFalse(otp.is_verified)
    
    def test_otp_verification(self):
        """Test OTP verification"""
        otp = OTP.objects.create(
            user=self.user,
            otp_code='123456',
            purpose='login'
        )
        otp.is_verified = True
        otp.save()
        self.assertTrue(otp.is_verified)


class AuthenticationAPITest(APITestCase):
    """Test cases for authentication APIs"""
    
    def setUp(self):
        self.send_otp_url = reverse('authentication:send-otp')
        self.verify_otp_url = reverse('authentication:verify-otp')
        self.refresh_url = reverse('authentication:refresh')
        self.logout_url = reverse('authentication:logout')
        
        self.user_data = {
            'phone': '+1234567890',
            'name': 'Test User',
            'role': 'patient'
        }
    
    def test_send_otp_new_user(self):
        """Test sending OTP to new user"""
        data = {
            'phone': '+1234567890',
            'name': 'New User',
            'role': 'patient'
        }
        response = self.client.post(self.send_otp_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertTrue(User.objects.filter(phone=data['phone']).exists())
    
    def test_send_otp_existing_user(self):
        """Test sending OTP to existing user"""
        user = User.objects.create_user(**self.user_data)
        data = {'phone': user.phone}
        response = self.client.post(self.send_otp_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
    
    def test_send_otp_invalid_phone(self):
        """Test sending OTP with invalid phone"""
        data = {'phone': 'invalid_phone'}
        response = self.client.post(self.send_otp_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    def test_verify_otp_success(self):
        """Test successful OTP verification"""
        user = User.objects.create_user(**self.user_data)
        otp = OTP.objects.create(
            user=user,
            otp_code='123456',
            purpose='login'
        )
        
        data = {
            'phone': user.phone,
            'otp_code': '123456'
        }
        response = self.client.post(self.verify_otp_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('access_token', response.data['data'])
        self.assertIn('refresh_token', response.data['data'])
    
    def test_verify_otp_invalid_code(self):
        """Test OTP verification with invalid code"""
        user = User.objects.create_user(**self.user_data)
        OTP.objects.create(
            user=user,
            otp_code='123456',
            purpose='login'
        )
        
        data = {
            'phone': user.phone,
            'otp_code': '654321'
        }
        response = self.client.post(self.verify_otp_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    def test_verify_otp_expired(self):
        """Test OTP verification with expired OTP"""
        user = User.objects.create_user(**self.user_data)
        otp = OTP.objects.create(
            user=user,
            otp_code='123456',
            purpose='login'
        )
        # Manually set expiry to past
        from django.utils import timezone
        from datetime import timedelta
        otp.expires_at = timezone.now() - timedelta(minutes=1)
        otp.save()
        
        data = {
            'phone': user.phone,
            'otp_code': '123456'
        }
        response = self.client.post(self.verify_otp_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])


class UtilsTest(TestCase):
    """Test cases for utility functions"""
    
    def test_generate_otp(self):
        """Test OTP generation"""
        otp = generate_otp()
        self.assertEqual(len(otp), 6)
        self.assertTrue(otp.isdigit())
    
    def test_generate_otp_custom_length(self):
        """Test OTP generation with custom length"""
        otp = generate_otp(length=4)
        self.assertEqual(len(otp), 4)
        self.assertTrue(otp.isdigit())


class UserSessionTest(TestCase):
    """Test cases for user session management"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            phone='+1234567890',
            name='Test User',
            role='patient'
        )
    
    def test_create_session(self):
        """Test session creation"""
        session = UserSession.objects.create(
            user=self.user,
            session_token='test_token_123',
            device_info='Test Device',
            ip_address='127.0.0.1'
        )
        self.assertEqual(session.user, self.user)
        self.assertEqual(session.session_token, 'test_token_123')
        self.assertTrue(session.is_active)
    
    def test_session_deactivation(self):
        """Test session deactivation"""
        session = UserSession.objects.create(
            user=self.user,
            session_token='test_token_123',
            device_info='Test Device',
            ip_address='127.0.0.1'
        )
        session.is_active = False
        session.save()
        self.assertFalse(session.is_active)


class PermissionTest(APITestCase):
    """Test cases for role-based permissions"""
    
    def setUp(self):
        self.patient = User.objects.create_user(
            phone='+1234567890',
            name='Patient User',
            role='patient'
        )
        self.doctor = User.objects.create_user(
            phone='+1234567891',
            name='Doctor User',
            role='doctor'
        )
        self.admin = User.objects.create_user(
            phone='+1234567892',
            name='Admin User',
            role='admin'
        )
    
    def test_patient_permissions(self):
        """Test patient role permissions"""
        self.client.force_authenticate(user=self.patient)
        # Add specific permission tests for patient role
        pass
    
    def test_doctor_permissions(self):
        """Test doctor role permissions"""
        self.client.force_authenticate(user=self.doctor)
        # Add specific permission tests for doctor role
        pass
    
    def test_admin_permissions(self):
        """Test admin role permissions"""
        self.client.force_authenticate(user=self.admin)
        # Add specific permission tests for admin role
        pass

