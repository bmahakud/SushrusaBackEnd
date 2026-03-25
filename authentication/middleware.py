
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class PatientProfileValidationMiddleware(MiddlewareMixin):
    """Middleware to validate patient profile consistency"""
    
    def process_request(self, request):
        """Process request to validate patient profiles"""
        # Skip for non-authenticated users
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return None
        
        # Only check for patient users
        if request.user.role != 'patient':
            return None
        
        # Check if patient has profile
        if not hasattr(request.user, 'patient_profile'):
            logger.warning(f"Patient {request.user.id} ({request.user.phone}) accessed API without PatientProfile")
            
            # For certain endpoints, return error
            if request.path.startswith('/api/patient/') or request.path.startswith('/api/admin/patients/'):
                return JsonResponse({
                    'success': False,
                    'error': {
                        'code': 'INCOMPLETE_PATIENT_ACCOUNT',
                        'message': 'Patient account is incomplete. Please complete your profile setup.',
                        'details': 'PatientProfile is missing for this account'
                    },
                    'timestamp': timezone.now().isoformat()
                }, status=400)
        
        return None
