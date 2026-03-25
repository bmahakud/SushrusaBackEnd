from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/doctor-status/$', consumers.DoctorStatusConsumer.as_asgi()),
    re_path(r'ws/doctor-superadmin/$', consumers.DoctorSuperAdminConsumer.as_asgi()),
    re_path(r'ws/notifications/$', consumers.NotificationConsumer.as_asgi()),
    re_path(r'ws/consultations/$', consumers.ConsultationConsumer.as_asgi()),
] 