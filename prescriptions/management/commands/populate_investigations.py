from django.core.management.base import BaseCommand
from prescriptions.models import InvestigationCategory, InvestigationTest


class Command(BaseCommand):
    help = 'Populate database with common investigation tests and categories'

    def handle(self, *args, **options):
        self.stdout.write('Creating investigation categories and tests...')
        
        # Create categories
        categories_data = [
            {
                'name': 'Blood Tests',
                'description': 'Laboratory blood analysis tests',
                'order': 1
            },
            {
                'name': 'Imaging Tests',
                'description': 'X-ray, CT scan, MRI, and ultrasound tests',
                'order': 2
            },
            {
                'name': 'Cardiac Tests',
                'description': 'Heart and cardiovascular system tests',
                'order': 3
            },
            {
                'name': 'Urine Tests',
                'description': 'Urine analysis and kidney function tests',
                'order': 4
            },
            {
                'name': 'Stool Tests',
                'description': 'Stool analysis and digestive system tests',
                'order': 5
            },
            {
                'name': 'Biopsy Tests',
                'description': 'Tissue sample analysis tests',
                'order': 6
            }
        ]
        
        categories = {}
        for cat_data in categories_data:
            category, created = InvestigationCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            categories[cat_data['name']] = category
            if created:
                self.stdout.write(f'Created category: {category.name}')
            else:
                self.stdout.write(f'Category already exists: {category.name}')
        
        # Create blood tests
        blood_tests = [
            {
                'name': 'Complete Blood Count (CBC)',
                'code': 'CBC',
                'description': 'Measures red blood cells, white blood cells, and platelets',
                'normal_range': 'RBC: 4.5-5.5M/μL, WBC: 4.5-11K/μL, Platelets: 150-450K/μL',
                'unit': 'Various',
                'is_fasting_required': False,
                'preparation_instructions': 'No special preparation required',
                'estimated_cost': 500.00
            },
            {
                'name': 'Hemoglobin A1c',
                'code': 'HbA1c',
                'description': 'Measures average blood sugar over 2-3 months',
                'normal_range': '4.0-5.6%',
                'unit': '%',
                'is_fasting_required': False,
                'preparation_instructions': 'No fasting required',
                'estimated_cost': 800.00
            },
            {
                'name': 'Fasting Blood Sugar',
                'code': 'FBS',
                'description': 'Measures blood glucose level after fasting',
                'normal_range': '70-100 mg/dL',
                'unit': 'mg/dL',
                'is_fasting_required': True,
                'preparation_instructions': 'Fast for 8-12 hours before test',
                'estimated_cost': 300.00
            },
            {
                'name': 'Lipid Profile',
                'code': 'LIPID',
                'description': 'Measures cholesterol and triglyceride levels',
                'normal_range': 'Total Cholesterol: <200 mg/dL, HDL: >40 mg/dL, LDL: <100 mg/dL',
                'unit': 'mg/dL',
                'is_fasting_required': True,
                'preparation_instructions': 'Fast for 12-14 hours before test',
                'estimated_cost': 600.00
            },
            {
                'name': 'Liver Function Test',
                'code': 'LFT',
                'description': 'Measures liver enzymes and proteins',
                'normal_range': 'ALT: 7-55 U/L, AST: 8-48 U/L, Bilirubin: 0.3-1.2 mg/dL',
                'unit': 'U/L, mg/dL',
                'is_fasting_required': False,
                'preparation_instructions': 'No special preparation required',
                'estimated_cost': 700.00
            },
            {
                'name': 'Kidney Function Test',
                'code': 'KFT',
                'description': 'Measures kidney function and electrolyte levels',
                'normal_range': 'Creatinine: 0.7-1.3 mg/dL, BUN: 7-20 mg/dL',
                'unit': 'mg/dL',
                'is_fasting_required': False,
                'preparation_instructions': 'No special preparation required',
                'estimated_cost': 600.00
            },
            {
                'name': 'Thyroid Function Test',
                'code': 'TFT',
                'description': 'Measures thyroid hormone levels',
                'normal_range': 'TSH: 0.4-4.0 mIU/L, T4: 5.0-12.0 μg/dL',
                'unit': 'mIU/L, μg/dL',
                'is_fasting_required': False,
                'preparation_instructions': 'No special preparation required',
                'estimated_cost': 1000.00
            }
        ]
        
        for test_data in blood_tests:
            test, created = InvestigationTest.objects.get_or_create(
                name=test_data['name'],
                category=categories['Blood Tests'],
                defaults=test_data
            )
            if created:
                self.stdout.write(f'Created blood test: {test.name}')
            else:
                self.stdout.write(f'Blood test already exists: {test.name}')
        
        # Create imaging tests
        imaging_tests = [
            {
                'name': 'Chest X-Ray',
                'code': 'CXR',
                'description': 'X-ray image of the chest to examine lungs and heart',
                'normal_range': 'Normal lung fields, normal cardiac silhouette',
                'unit': 'N/A',
                'is_fasting_required': False,
                'preparation_instructions': 'Remove metal objects, wear hospital gown',
                'estimated_cost': 800.00
            },
            {
                'name': 'CT Scan - Chest',
                'code': 'CT-CHEST',
                'description': 'Detailed cross-sectional images of the chest',
                'normal_range': 'Normal lung parenchyma, no masses or nodules',
                'unit': 'N/A',
                'is_fasting_required': False,
                'preparation_instructions': 'May require contrast dye, remove metal objects',
                'estimated_cost': 3000.00
            },
            {
                'name': 'MRI - Brain',
                'code': 'MRI-BRAIN',
                'description': 'Detailed images of the brain and surrounding structures',
                'normal_range': 'Normal brain parenchyma, no mass lesions',
                'unit': 'N/A',
                'is_fasting_required': False,
                'preparation_instructions': 'Remove all metal objects, may require contrast',
                'estimated_cost': 5000.00
            },
            {
                'name': 'Ultrasound - Abdomen',
                'code': 'US-ABD',
                'description': 'Sound wave images of abdominal organs',
                'normal_range': 'Normal organ size and echogenicity',
                'unit': 'N/A',
                'is_fasting_required': True,
                'preparation_instructions': 'Fast for 6-8 hours before test',
                'estimated_cost': 1500.00
            }
        ]
        
        for test_data in imaging_tests:
            test, created = InvestigationTest.objects.get_or_create(
                name=test_data['name'],
                category=categories['Imaging Tests'],
                defaults=test_data
            )
            if created:
                self.stdout.write(f'Created imaging test: {test.name}')
            else:
                self.stdout.write(f'Imaging test already exists: {test.name}')
        
        # Create cardiac tests
        cardiac_tests = [
            {
                'name': 'Electrocardiogram (ECG)',
                'code': 'ECG',
                'description': 'Records electrical activity of the heart',
                'normal_range': 'Normal sinus rhythm, normal intervals',
                'unit': 'N/A',
                'is_fasting_required': False,
                'preparation_instructions': 'No special preparation required',
                'estimated_cost': 500.00
            },
            {
                'name': 'Echocardiogram',
                'code': 'ECHO',
                'description': 'Ultrasound of the heart to assess function',
                'normal_range': 'Normal ejection fraction >55%, normal valve function',
                'unit': 'N/A',
                'is_fasting_required': False,
                'preparation_instructions': 'No special preparation required',
                'estimated_cost': 2500.00
            },
            {
                'name': 'Stress Test',
                'code': 'STRESS',
                'description': 'Exercise test to assess heart function under stress',
                'normal_range': 'Normal exercise tolerance, no ECG changes',
                'unit': 'N/A',
                'is_fasting_required': True,
                'preparation_instructions': 'Fast for 4 hours, wear comfortable clothes',
                'estimated_cost': 4000.00
            }
        ]
        
        for test_data in cardiac_tests:
            test, created = InvestigationTest.objects.get_or_create(
                name=test_data['name'],
                category=categories['Cardiac Tests'],
                defaults=test_data
            )
            if created:
                self.stdout.write(f'Created cardiac test: {test.name}')
            else:
                self.stdout.write(f'Cardiac test already exists: {test.name}')
        
        # Create urine tests
        urine_tests = [
            {
                'name': 'Urine Analysis',
                'code': 'UA',
                'description': 'Examines urine for various substances and cells',
                'normal_range': 'pH: 4.5-8.0, Specific Gravity: 1.005-1.030',
                'unit': 'Various',
                'is_fasting_required': False,
                'preparation_instructions': 'Clean catch midstream urine sample',
                'estimated_cost': 300.00
            },
            {
                'name': '24-Hour Urine Collection',
                'code': '24H-URINE',
                'description': 'Collects urine over 24 hours for detailed analysis',
                'normal_range': 'Varies by substance being measured',
                'unit': 'Various',
                'is_fasting_required': False,
                'preparation_instructions': 'Collect all urine for 24 hours',
                'estimated_cost': 800.00
            }
        ]
        
        for test_data in urine_tests:
            test, created = InvestigationTest.objects.get_or_create(
                name=test_data['name'],
                category=categories['Urine Tests'],
                defaults=test_data
            )
            if created:
                self.stdout.write(f'Created urine test: {test.name}')
            else:
                self.stdout.write(f'Urine test already exists: {test.name}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully populated investigation tests and categories!')
        )
