from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from patients.models import MedicalRecord, PatientDocument, PatientNote
from datetime import date, timedelta
import os

User = get_user_model()

class Command(BaseCommand):
    help = 'Create sample medical records, documents, and notes for a patient'

    def add_arguments(self, parser):
        parser.add_argument('phone', type=str, help='Patient phone number')
        parser.add_argument('--clear', action='store_true', help='Clear existing data before creating new data')

    def handle(self, *args, **options):
        phone = options['phone']
        clear_existing = options['clear']

        try:
            # Find the patient by phone number
            patient = User.objects.get(phone=phone, role='patient')
            self.stdout.write(f"Found patient: {patient.name} ({patient.phone})")

            if clear_existing:
                # Clear existing data
                MedicalRecord.objects.filter(patient=patient).delete()
                PatientDocument.objects.filter(patient=patient).delete()
                PatientNote.objects.filter(patient=patient).delete()
                self.stdout.write("Cleared existing data")

            # Create sample medical records
            medical_records_data = [
                {
                    'record_type': 'diagnosis',
                    'title': 'Diabetes Type 2 Diagnosis',
                    'description': 'Patient diagnosed with Type 2 Diabetes Mellitus. Blood sugar levels elevated. Prescribed Metformin 500mg twice daily. Regular monitoring required.',
                    'date_recorded': date.today() - timedelta(days=30)
                },
                {
                    'record_type': 'lab_report',
                    'title': 'Blood Sugar Test Results',
                    'description': 'Fasting blood sugar: 180 mg/dL (High), Postprandial: 220 mg/dL (High). HbA1c: 8.2% (High). Requires immediate attention and medication adjustment.',
                    'date_recorded': date.today() - timedelta(days=25)
                },
                {
                    'record_type': 'prescription',
                    'title': 'Diabetes Medication Prescription',
                    'description': 'Metformin 500mg twice daily with meals. Glimepiride 1mg once daily in the morning. Monitor blood sugar levels regularly.',
                    'date_recorded': date.today() - timedelta(days=20)
                },
                {
                    'record_type': 'vaccination',
                    'title': 'COVID-19 Vaccination Record',
                    'description': 'First dose: Covishield on 15th March 2024. Second dose: Covishield on 15th April 2024. No adverse reactions reported.',
                    'date_recorded': date.today() - timedelta(days=90)
                },
                {
                    'record_type': 'allergy',
                    'title': 'Penicillin Allergy Record',
                    'description': 'Patient has severe allergic reaction to Penicillin. Symptoms include rash, swelling, and difficulty breathing. Avoid all penicillin-based medications.',
                    'date_recorded': date.today() - timedelta(days=60)
                }
            ]

            for record_data in medical_records_data:
                MedicalRecord.objects.create(
                    patient=patient,
                    recorded_by=patient,  # Self-recorded for demo
                    **record_data
                )

            self.stdout.write(f"Created {len(medical_records_data)} medical records")

            # Create sample documents
            documents_data = [
                {
                    'document_type': 'id_proof',
                    'title': 'Aadhaar Card',
                    'description': 'Patient\'s Aadhaar card for identity verification. Valid until 2030.',
                    'file': 'documents/aadhaar_sample.pdf'
                },
                {
                    'document_type': 'insurance',
                    'title': 'Health Insurance Policy',
                    'description': 'Comprehensive health insurance policy covering hospitalization and outpatient care. Policy number: HI123456789',
                    'file': 'documents/insurance_policy.pdf'
                },
                {
                    'document_type': 'lab_report',
                    'title': 'Complete Blood Count Report',
                    'description': 'Recent CBC report showing normal ranges for all parameters. Hemoglobin: 14.2 g/dL, WBC: 7,500/μL',
                    'file': 'documents/cbc_report.pdf'
                },
                {
                    'document_type': 'prescription',
                    'title': 'Diabetes Management Prescription',
                    'description': 'Current prescription for diabetes management including Metformin and Glimepiride.',
                    'file': 'documents/diabetes_prescription.pdf'
                }
            ]

            for doc_data in documents_data:
                PatientDocument.objects.create(
                    patient=patient,
                    **doc_data
                )

            self.stdout.write(f"Created {len(documents_data)} documents")

            # Create sample notes
            notes_data = [
                {
                    'note': 'Patient shows good compliance with diabetes medication. Blood sugar levels have improved from last visit. Continue current medication regimen.',
                    'is_private': False
                },
                {
                    'note': 'Patient reported mild dizziness after taking Glimepiride. Advised to take with food and monitor symptoms. Consider dosage adjustment if symptoms persist.',
                    'is_private': True
                },
                {
                    'note': 'Patient needs to schedule follow-up appointment in 2 weeks for blood sugar monitoring. Also need to check kidney function tests.',
                    'is_private': False
                },
                {
                    'note': 'Patient expressed concerns about medication side effects. Provided counseling about diabetes management and lifestyle modifications.',
                    'is_private': True
                },
                {
                    'note': 'Patient has been following diet recommendations well. Weight has reduced by 2kg in the last month. Continue with current diet plan.',
                    'is_private': False
                }
            ]

            for note_data in notes_data:
                PatientNote.objects.create(
                    patient=patient,
                    created_by=patient,  # Self-created for demo
                    **note_data
                )

            self.stdout.write(f"Created {len(notes_data)} notes")

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created sample data for patient {patient.name}:\n'
                    f'- {len(medical_records_data)} medical records\n'
                    f'- {len(documents_data)} documents\n'
                    f'- {len(notes_data)} notes'
                )
            )

        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Patient with phone number {phone} not found')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating sample data: {str(e)}')
            )
