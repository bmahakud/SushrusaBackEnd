from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from .models import Notification
from .serializers import NotificationSerializer, NotificationStatsSerializer

class NotificationListView(generics.ListAPIView):
    """
    List all notifications with filtering and pagination
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['type', 'category', 'is_read', 'action_required']
    search_fields = ['title', 'message']
    ordering_fields = ['created_at', 'type', 'category']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Notification.objects.all()
    
    @extend_schema(
        summary="List Notifications",
        description="Get a paginated list of notifications with filtering options",
        parameters=[
            OpenApiParameter(name="type", type=OpenApiTypes.STR, description="Filter by notification type"),
            OpenApiParameter(name="category", type=OpenApiTypes.STR, description="Filter by category"),
            OpenApiParameter(name="is_read", type=OpenApiTypes.BOOL, description="Filter by read status"),
            OpenApiParameter(name="action_required", type=OpenApiTypes.BOOL, description="Filter by action required"),
            OpenApiParameter(name="search", type=OpenApiTypes.STR, description="Search in title and message"),
            OpenApiParameter(name="ordering", type=OpenApiTypes.STR, description="Order by field"),
        ],
        responses={200: NotificationSerializer}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class NotificationDetailView(generics.RetrieveAPIView):
    """
    Retrieve a specific notification
    """
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Get Notification",
        description="Retrieve a specific notification by ID"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
@extend_schema(
    summary="Mark Notification as Read",
    description="Mark a specific notification as read"
)
def mark_notification_read(request, notification_id):
    """
    Mark a notification as read
    """
    try:
        notification = Notification.objects.get(id=notification_id)
        notification.mark_as_read()
        return Response({
            'success': True,
            'message': 'Notification marked as read',
            'data': NotificationSerializer(notification).data
        })
    except Notification.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Notification not found'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@extend_schema(
    summary="Mark All Notifications as Read",
    description="Mark all notifications as read"
)
def mark_all_notifications_read(request):
    """
    Mark all notifications as read
    """
    Notification.objects.filter(is_read=False).update(is_read=True)
    return Response({
        'success': True,
        'message': 'All notifications marked as read'
    })

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@extend_schema(
    summary="Delete Notification",
    description="Delete a specific notification"
)
def delete_notification(request, notification_id):
    """
    Delete a notification
    """
    try:
        notification = Notification.objects.get(id=notification_id)
        notification.delete()
        return Response({
            'success': True,
            'message': 'Notification deleted successfully'
        })
    except Notification.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Notification not found'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@extend_schema(
    summary="Get Notification Statistics",
    description="Get notification statistics including counts",
    responses={200: NotificationStatsSerializer}
)
def notification_stats(request):
    """
    Get notification statistics
    """
    stats = {
        'total': Notification.objects.count(),
        'unread': Notification.get_unread_count(),
        'critical': Notification.get_critical_count(),
        'action_required': Notification.get_action_required_count(),
    }
    
    serializer = NotificationStatsSerializer(stats)
    return Response({
        'success': True,
        'data': serializer.data
    })

# Helper functions to create notifications from other parts of the system
def create_system_notification(title, message, notification_type='info', action_required=False, action_url=None, metadata=None):
    """Create a system notification"""
    return Notification.create_notification(
        type=notification_type,
        title=title,
        message=message,
        category='system',
        action_required=action_required,
        action_url=action_url,
        metadata=metadata
    )

def create_doctor_notification(title, message, notification_type='important', action_required=False, action_url=None, metadata=None):
    """Create a doctor-related notification"""
    return Notification.create_notification(
        type=notification_type,
        title=title,
        message=message,
        category='doctors',
        action_required=action_required,
        action_url=action_url,
        metadata=metadata
    )

def create_clinic_notification(title, message, notification_type='important', action_required=False, action_url=None, metadata=None):
    """Create a clinic-related notification"""
    return Notification.create_notification(
        type=notification_type,
        title=title,
        message=message,
        category='clinics',
        action_required=action_required,
        action_url=action_url,
        metadata=metadata
    )

def create_payment_notification(title, message, notification_type='success', action_required=False, action_url=None, metadata=None):
    """Create a payment-related notification"""
    return Notification.create_notification(
        type=notification_type,
        title=title,
        message=message,
        category='payments',
        action_required=action_required,
        action_url=action_url,
        metadata=metadata
    )

def create_security_notification(title, message, notification_type='critical', action_required=True, action_url=None, metadata=None):
    """Create a security-related notification"""
    return Notification.create_notification(
        type=notification_type,
        title=title,
        message=message,
        category='security',
        action_required=action_required,
        action_url=action_url,
        metadata=metadata
    ) 