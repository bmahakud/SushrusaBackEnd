from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import DoctorSlotViewSet, SuperAdminDoctorManagementView, SuperAdminDoctorDetailView, DoctorStatusListView, DoctorStatusStatsView, DoctorStatusUpdateView, DoctorStatusDetailView, DoctorStatusOfflineView, AdminSlotsView

app_name = 'doctors'

# Create router for ViewSets
router = DefaultRouter()
router.register(r'', views.DoctorProfileViewSet, basename='doctor-profile')

urlpatterns = [
    # Test endpoints (development only)
    path('test-detail/<str:doctor_id>/', views.test_doctor_detail, name='test-doctor-detail'),
    path('test-superadmin-detail/<str:doctor_id>/', views.test_superadmin_doctor_detail, name='test-superadmin-doctor-detail'),
    
    # Public Doctor Listing (no authentication required)
    path('public/', views.PublicDoctorListView.as_view(), name='public-doctor-list'),
    
    # Doctor Status URLs (must come before router to avoid conflicts)
    path('status/', DoctorStatusListView.as_view(), name='doctor-status-list'),
    path('status/stats/', DoctorStatusStatsView.as_view(), name='doctor-status-stats'),
    path('status/update/', DoctorStatusUpdateView.as_view(), name='doctor-status-update'),
    path('status/offline/', DoctorStatusOfflineView.as_view(), name='doctor-status-offline'),
    path('status/<int:doctor_id>/', DoctorStatusDetailView.as_view(), name='doctor-status-detail'),
    
    # SuperAdmin Doctor Management
    path('superadmin/', SuperAdminDoctorManagementView.as_view(), name='superadmin-doctor-list'),
    path('superadmin/<str:doctor_id>/', SuperAdminDoctorDetailView.as_view(), name='superadmin-doctor-detail'),
    
    # Doctor search and statistics
    path('search/', views.DoctorSearchView.as_view(), name='doctor-search'),
    path('stats/', views.DoctorStatsView.as_view(), name='doctor-stats'),
    
    # Admin slots management
    path('admin/slots/', AdminSlotsView.as_view(), name='admin-slots'),
    
    # Doctor-specific nested resources
    path('<str:doctor_id>/education/', 
         views.DoctorEducationViewSet.as_view({'get': 'list', 'post': 'create'}), 
         name='doctor-education'),
    path('<str:doctor_id>/education/<int:pk>/', 
         views.DoctorEducationViewSet.as_view({
             'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
         }), 
         name='doctor-education-detail'),
    
    path('<str:doctor_id>/experience/', 
         views.DoctorExperienceViewSet.as_view({'get': 'list', 'post': 'create'}), 
         name='doctor-experience'),
    path('<str:doctor_id>/experience/<int:pk>/', 
         views.DoctorExperienceViewSet.as_view({
             'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
         }), 
         name='doctor-experience-detail'),
    
    path('<str:doctor_id>/documents/', 
         views.DoctorDocumentViewSet.as_view({'get': 'list', 'post': 'create'}), 
         name='doctor-documents'),
    path('<str:doctor_id>/documents/<int:pk>/', 
         views.DoctorDocumentViewSet.as_view({
             'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
         }), 
         name='doctor-document-detail'),
    
    path('<str:doctor_id>/schedule/', 
         views.DoctorScheduleViewSet.as_view({'get': 'list', 'post': 'create'}), 
         name='doctor-schedule'),
    path('<str:doctor_id>/schedule/<int:pk>/', 
         views.DoctorScheduleViewSet.as_view({
             'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
         }), 
         name='doctor-schedule-detail'),
    
    path('<str:doctor_id>/reviews/', 
         views.DoctorReviewViewSet.as_view({'get': 'list', 'post': 'create'}), 
         name='doctor-reviews'),
    path('<str:doctor_id>/reviews/<int:pk>/', 
         views.DoctorReviewViewSet.as_view({
             'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
         }), 
         name='doctor-review-detail'),
    
    # Include router URLs for main doctor profile operations
    path('', include(router.urls)),
]

urlpatterns += [
    path('<str:doctor_id>/slots/',
         DoctorSlotViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='doctor-slot-list'),
    path('<str:doctor_id>/slots/<int:pk>/',
         DoctorSlotViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
         name='doctor-slot-detail'),
]



