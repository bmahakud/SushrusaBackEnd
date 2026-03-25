from django.urls import path
from . import views

app_name = 'utils'

urlpatterns = [
    path('signed-url/', views.SignedUrlView.as_view(), name='signed-url'),
    path('signature/', views.SignatureUploadView.as_view(), name='signature-upload'),
]
