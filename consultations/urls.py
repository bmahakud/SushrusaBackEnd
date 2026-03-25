from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'consultations'

# Create router for ViewSets
router = DefaultRouter()
router.register(r'', views.ConsultationViewSet, basename='consultation')

doctor_router = DefaultRouter()
doctor_router.register(r'', views.DoctorConsultationViewSet, basename='doctor-consultation')

urlpatterns = [
    # Patient-specific consultation endpoints
    path('patient/consultations/', views.PatientConsultationView.as_view(), name='patient-consultations'),
    
    # Consultation search and statistics
    path('search/', views.ConsultationSearchView.as_view(), name='consultation-search'),
    path('stats/', views.ConsultationStatsView.as_view(), name='consultation-stats'),
    
    # Overdue consultations endpoint
    path('overdue/', views.OverdueConsultationsView.as_view(), name='overdue-consultations'),
    
    # Consultation-specific nested resources
    path('<str:consultation_id>/diagnosis/', 
         views.ConsultationDiagnosisViewSet.as_view({'get': 'list', 'post': 'create'}), 
         name='consultation-diagnosis'),
    path('<str:consultation_id>/diagnosis/<int:pk>/', 
         views.ConsultationDiagnosisViewSet.as_view({
             'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
         }), 
         name='consultation-diagnosis-detail'),
    
    path('<str:consultation_id>/vital-signs/', 
         views.ConsultationVitalSignsViewSet.as_view({"get": "list", "post": "create"}), 
         name='consultation-vital-signs'),
    path('<str:consultation_id>/vital-signs/<int:pk>/', 
         views.ConsultationVitalSignsViewSet.as_view({
             "get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"
         }), 
         name='consultation-vital-signs-detail'),
    
    path('<str:consultation_id>/documents/', 
         views.ConsultationAttachmentViewSet.as_view({'get': 'list', 'post': 'create'}), 
         name='consultation-documents'),
    path('<str:consultation_id>/documents/<int:pk>/', 
         views.ConsultationAttachmentViewSet.as_view({
             'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
         }), 
         name='consultation-document-detail'),
    
    path('<str:consultation_id>/notes/', 
         views.ConsultationNoteViewSet.as_view({'get': 'list', 'post': 'create'}), 
         name='consultation-notes'),
    path('<str:consultation_id>/notes/<int:pk>/', 
         views.ConsultationNoteViewSet.as_view({
             'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
         }), 
         name='consultation-note-detail'),
    
    path('<str:consultation_id>/symptoms/', 
         views.ConsultationSymptomViewSet.as_view({'get': 'list', 'post': 'create'}), 
         name='consultation-symptoms'),
    path('<str:consultation_id>/symptoms/<int:pk>/', 
         views.ConsultationSymptomViewSet.as_view({
             'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
         }), 
         name='consultation-symptom-detail'),
    
    # Get prescription for consultation
    path('<str:consultation_id>/prescription/', 
         views.ConsultationPrescriptionView.as_view(), 
         name='consultation-prescription'),
    
    # Get receipt for consultation
    path('<str:consultation_id>/receipt/', 
         views.ConsultationReceiptView.as_view(), 
         name='consultation-receipt'),
    
    # Check-in management endpoints
    path('<str:consultation_id>/check-in/', 
         views.ConsultationCheckInView.as_view(), 
         name='consultation-check-in'),
    path('<str:consultation_id>/ready/', 
         views.ConsultationReadyView.as_view(), 
         name='consultation-ready'),
    path('<str:consultation_id>/start/', 
         views.ConsultationStartView.as_view(), 
         name='consultation-start'),
    path('<str:consultation_id>/complete/', 
         views.ConsultationCompleteView.as_view(), 
         name='consultation-complete'),
    
    # Admin consultation management
    path('admin/management/', 
         views.ConsultationManagementView.as_view(), 
         name='admin-consultation-management'),
    
    # SuperAdmin consultation management with advanced filtering
    path('superadmin/management/', 
         views.SuperAdminConsultationManagementView.as_view(), 
         name='superadmin-consultation-management'),
    
    # Doctor consultations
    path('doctor/', include(doctor_router.urls)),
    
    # Enhanced consultation endpoints for doctors (must come before router includes)
    path('statistics/', views.ConsultationStatsView.as_view(), name='consultation-statistics'),
    path('analytics/', views.ConsultationStatsView.as_view(), name='consultation-analytics'),
    path('real-time-updates/', views.ConsultationStatsView.as_view(), name='consultation-real-time-updates'),
    
    # Test endpoints (development only)
    path('test-admin-permissions/', views.test_admin_permissions, name='test-admin-permissions'),
    path('test-admin-consultation-access/', views.test_admin_consultation_access, name='test-admin-consultation-access'),
    path('test-list/', views.test_consultation_list, name='test-consultation-list'),
    path('test-detail/<str:consultation_id>/', views.test_consultation_detail, name='test-consultation-detail'),
    path('test-receipt/<str:consultation_id>/', views.test_generate_receipt, name='test-generate-receipt'),
    path('test-whatsapp/', views.test_whatsapp_notification, name='test-whatsapp-notification'),
    path('test-available-slots/', views.test_calculate_available_slots, name='test-calculate-available-slots'),
    
    # Include router URLs for main consultation operations (must come last)
    path('', include(router.urls)),
]

