"""
Signals for automatic file upload to DigitalOcean Spaces
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
from .models import Consultation, ConsultationNote, ConsultationVitalSigns, ConsultationDiagnosis

channel_layer = get_channel_layer()

@receiver(post_save, sender=Consultation)
def consultation_status_change_notification(sender, instance, created, **kwargs):
    """Send real-time notification when consultation status changes"""
    if created:
        # New consultation created
        notification_data = {
            'type': 'consultation_created',
            'consultation_id': instance.id,
            'patient_name': instance.patient.name,
            'doctor_name': instance.doctor.name,
            'scheduled_date': instance.scheduled_date.isoformat(),
            'scheduled_time': instance.scheduled_time.isoformat(),
            'status': instance.status,
            'timestamp': timezone.now().isoformat()
        }
    else:
        # Consultation updated
        notification_data = {
            'type': 'consultation_updated',
            'consultation_id': instance.id,
            'patient_name': instance.patient.name,
            'doctor_name': instance.doctor.name,
            'status': instance.status,
            'timestamp': timezone.now().isoformat()
        }
    
    # Send to doctor's personal channel
    doctor_channel = f"doctor_{instance.doctor.id}"
    async_to_sync(channel_layer.group_send)(
        doctor_channel,
        {
            'type': 'consultation_notification',
            'message': notification_data
        }
    )
    
    # Send to patient's personal channel
    patient_channel = f"patient_{instance.patient.id}"
    async_to_sync(channel_layer.group_send)(
        patient_channel,
        {
            'type': 'consultation_notification',
            'message': notification_data
        }
    )

@receiver(post_save, sender=ConsultationNote)
def consultation_note_notification(sender, instance, created, **kwargs):
    """Send notification when consultation notes are added"""
    if created:
        notification_data = {
            'type': 'consultation_note_added',
            'consultation_id': instance.consultation.id,
            'note_type': instance.note_type,
            'created_by': instance.created_by.name,
            'timestamp': timezone.now().isoformat()
        }
        
        # Send to doctor
        doctor_channel = f"doctor_{instance.consultation.doctor.id}"
        async_to_sync(channel_layer.group_send)(
            doctor_channel,
            {
                'type': 'consultation_notification',
                'message': notification_data
            }
        )

@receiver(post_save, sender=ConsultationVitalSigns)
def vital_signs_notification(sender, instance, created, **kwargs):
    """Send notification when vital signs are recorded"""
    if created:
        notification_data = {
            'type': 'vital_signs_recorded',
            'consultation_id': instance.consultation.id,
            'patient_name': instance.consultation.patient.name,
            'recorded_by': instance.recorded_by.name if instance.recorded_by else 'System',
            'timestamp': timezone.now().isoformat()
        }
        
        # Send to doctor
        doctor_channel = f"doctor_{instance.consultation.doctor.id}"
        async_to_sync(channel_layer.group_send)(
            doctor_channel,
            {
                'type': 'consultation_notification',
                'message': notification_data
            }
        )

@receiver(post_save, sender=ConsultationDiagnosis)
def diagnosis_notification(sender, instance, created, **kwargs):
    """Send notification when diagnosis is added"""
    if created:
        notification_data = {
            'type': 'diagnosis_added',
            'consultation_id': instance.consultation.id,
            'diagnosis': instance.diagnosis,
            'diagnosis_type': instance.diagnosis_type,
            'timestamp': timezone.now().isoformat()
        }
        
        # Send to doctor
        doctor_channel = f"doctor_{instance.consultation.doctor.id}"
        async_to_sync(channel_layer.group_send)(
            doctor_channel,
            {
                'type': 'consultation_notification',
                'message': notification_data
            }
        )

@receiver(post_delete, sender=Consultation)
def consultation_deleted_notification(sender, instance, **kwargs):
    """Send notification when consultation is deleted"""
    notification_data = {
        'type': 'consultation_deleted',
        'consultation_id': instance.id,
        'patient_name': instance.patient.name,
        'doctor_name': instance.doctor.name,
        'timestamp': timezone.now().isoformat()
    }
    
    # Send to doctor's personal channel
    doctor_channel = f"doctor_{instance.doctor.id}"
    async_to_sync(channel_layer.group_send)(
        doctor_channel,
        {
            'type': 'consultation_notification',
            'message': notification_data
        }
    )
    
    # Send to patient's personal channel
    patient_channel = f"patient_{instance.patient.id}"
    async_to_sync(channel_layer.group_send)(
        patient_channel,
        {
            'type': 'consultation_notification',
            'message': notification_data
        }
    ) 