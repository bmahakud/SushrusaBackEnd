from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from .signed_urls import get_signed_media_url
from django.utils import timezone
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
import uuid

class SignedUrlView(APIView):
    """Generate signed URLs for file downloads"""
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        parameters=[
            OpenApiParameter('file_path', OpenApiTypes.STR, description='File path to generate signed URL for'),
        ],
        responses={200: dict},
        description="Generate a signed URL for file download"
    )
    def get(self, request):
        """Generate signed URL for file download"""
        file_path = request.query_params.get('file_path')
        
        if not file_path:
            return Response({
                'success': False,
                'error': {
                    'code': 'MISSING_PARAMETER',
                    'message': 'file_path parameter is required'
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            signed_url = get_signed_media_url(file_path)
            
            return Response({
                'success': True,
                'data': {
                    'signed_url': signed_url,
                    'file_path': file_path,
                    'expires_in': 3600  # 1 hour
                },
                'message': 'Signed URL generated successfully',
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': {
                    'code': 'SIGNED_URL_ERROR',
                    'message': f'Error generating signed URL: {str(e)}'
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SignatureUploadView(APIView):
    """Upload signature files to Digital Ocean"""
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'signature': {
                        'type': 'string',
                        'format': 'binary',
                        'description': 'Signature file (image or PDF)'
                    },
                    'type': {
                        'type': 'string',
                        'description': 'Type of signature (e.g., doctor_signature)'
                    }
                },
                'required': ['signature']
            }
        },
        responses={
            200: {
                'description': 'Signature uploaded successfully',
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'object',
                            'properties': {
                                'success': {'type': 'boolean'},
                                'data': {
                                    'type': 'object',
                                    'properties': {
                                        'url': {'type': 'string'},
                                        'file_path': {'type': 'string'}
                                    }
                                },
                                'message': {'type': 'string'},
                                'timestamp': {'type': 'string'}
                            }
                        }
                    }
                }
            },
            400: {
                'description': 'Invalid file or missing parameters',
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'object',
                            'properties': {
                                'success': {'type': 'boolean'},
                                'error': {'type': 'object'},
                                'timestamp': {'type': 'string'}
                            }
                        }
                    }
                }
            }
        },
        description="Upload signature file to Digital Ocean storage"
    )
    def post(self, request):
        """Upload signature file"""
        signature_file = request.FILES.get('signature')
        signature_type = request.data.get('type', 'doctor_signature')
        
        if not signature_file:
            return Response({
                'success': False,
                'error': {
                    'code': 'MISSING_FILE',
                    'message': 'Signature file is required'
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate file type
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'application/pdf']
        if signature_file.content_type not in allowed_types:
            return Response({
                'success': False,
                'error': {
                    'code': 'INVALID_FILE_TYPE',
                    'message': 'Only JPEG, PNG, GIF, and PDF files are allowed'
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate file size (max 5MB)
        if signature_file.size > 5 * 1024 * 1024:
            return Response({
                'success': False,
                'error': {
                    'code': 'FILE_TOO_LARGE',
                    'message': 'File size must be less than 5MB'
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Generate unique filename
            file_extension = os.path.splitext(signature_file.name)[1]
            unique_filename = f"{signature_type}_{uuid.uuid4().hex}{file_extension}"
            file_path = f"signatures/{unique_filename}"
            
            # Save file to Digital Ocean
            saved_path = default_storage.save(file_path, ContentFile(signature_file.read()))
            
            # Generate signed URL
            signed_url = get_signed_media_url(saved_path)
            
            # Save signature information to DoctorSignature model if it's a doctor signature
            if signature_type == 'doctor_signature':
                try:
                    from doctors.models import DoctorSignature
                    # Get or create signature record for the doctor
                    signature_record, created = DoctorSignature.objects.get_or_create(
                        doctor=request.user,
                        defaults={
                            'signature_url': signed_url,
                            'file_path': saved_path,
                            'file_name': signature_file.name,
                            'file_size': signature_file.size,
                            'uploaded_by': request.user
                        }
                    )
                    
                    # Update if record already exists
                    if not created:
                        signature_record.signature_url = signed_url
                        signature_record.file_path = saved_path
                        signature_record.file_name = signature_file.name
                        signature_record.file_size = signature_file.size
                        signature_record.uploaded_by = request.user
                        signature_record.is_active = True
                        signature_record.save()
                        
                except Exception as e:
                    print(f"Error saving signature record: {e}")
            
            return Response({
                'success': True,
                'data': {
                    'url': signed_url,
                    'file_path': saved_path
                },
                'message': 'Signature uploaded successfully',
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': {
                    'code': 'UPLOAD_ERROR',
                    'message': f'Error uploading signature: {str(e)}'
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
