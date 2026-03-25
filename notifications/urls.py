from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    # List and retrieve notifications
    path('', views.NotificationListView.as_view(), name='notification-list'),
    path('<int:pk>/', views.NotificationDetailView.as_view(), name='notification-detail'),
    
    # Notification actions
    path('<int:notification_id>/mark-read/', views.mark_notification_read, name='mark-notification-read'),
    path('mark-all-read/', views.mark_all_notifications_read, name='mark-all-notifications-read'),
    path('<int:notification_id>/delete/', views.delete_notification, name='delete-notification'),
    
    # Statistics
    path('stats/', views.notification_stats, name='notification-stats'),
] 