from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'analytics'

# Create router for ViewSets
router = DefaultRouter()
router.register(r'user-analytics', views.UserAnalyticsViewSet, basename='user-analytics')
router.register(r'revenue-analytics', views.RevenueAnalyticsViewSet, basename='revenue-analytics')
router.register(r'doctor-performance', views.DoctorPerformanceViewSet, basename='doctor-performance')

urlpatterns = [
    # Dashboard and overview
    path('dashboard/', views.DashboardStatsView.as_view(), name='dashboard-stats'),
    path('detailed/', views.DetailedAnalyticsView.as_view(), name='detailed-analytics'),
    path('real-time/', views.RealTimeMetricsView.as_view(), name='real-time-metrics'),
    path('superadmin/overview/', views.SuperAdminOverviewStatsView.as_view(), name='superadmin-overview-stats'),
    
    # Doctor-specific analytics
    path('doctor/earnings/', views.DoctorEarningsView.as_view(), name='doctor-earnings'),
    
    # SuperAdmin comprehensive analytics
    path('superadmin/comprehensive/', views.SuperAdminComprehensiveAnalyticsView.as_view(), name='superadmin-comprehensive-analytics'),
    path('superadmin/revenue/', views.SuperAdminRevenueAnalyticsView.as_view(), name='superadmin-revenue-analytics'),
    path('superadmin/consultations/', views.SuperAdminConsultationAnalyticsView.as_view(), name='superadmin-consultation-analytics'),
    path('superadmin/patients/', views.SuperAdminPatientAnalyticsView.as_view(), name='superadmin-patient-analytics'),
    path('superadmin/clinics/', views.SuperAdminClinicAnalyticsView.as_view(), name='superadmin-clinic-analytics'),
    path('superadmin/doctors/', views.SuperAdminDoctorAnalyticsView.as_view(), name='superadmin-doctor-analytics'),
    
    # Specific analytics
    path('user-growth/', views.UserGrowthAnalyticsView.as_view(), name='user-growth'),
    path('consultations/', views.ConsultationAnalyticsView.as_view(), name='consultation-analytics'),
    path('revenue-report/', views.RevenueReportView.as_view(), name='revenue-report'),
    path('geographic/', views.GeographicAnalyticsView.as_view(), name='geographic-analytics'),
    
    # Custom reports and exports
    path('custom-report/', views.CustomReportView.as_view(), name='custom-report'),
    path('export/', views.ExportDataView.as_view(), name='export-data'),
    
    # ViewSet routes
    path('', include(router.urls)),
]

