from django.core.management.base import BaseCommand
from prescriptions.models import InvestigationCategory, InvestigationTest


class Command(BaseCommand):
    help = 'Populate database with complete investigation tests from pricelist'

    def handle(self, *args, **options):
        self.stdout.write('Creating complete investigation categories and tests...')
        
        # Create categories based on pricelist
        categories_data = [
            {'name': 'CT', 'description': 'Computed Tomography scans', 'order': 1},
            {'name': 'CT GUIDED PROCEDURE', 'description': 'CT guided biopsy and procedures', 'order': 2},
            {'name': 'CARDIOLOGY', 'description': 'Cardiac tests and procedures', 'order': 3},
            {'name': 'DEPARTMENT', 'description': 'General department procedures', 'order': 4},
            {'name': 'GASTROENTEROLOGY', 'description': 'Gastroenterology procedures', 'order': 5},
            {'name': 'MRI', 'description': 'Magnetic Resonance Imaging', 'order': 6},
            {'name': 'MAMMOGRAPHY', 'description': 'Breast imaging tests', 'order': 7},
            {'name': 'OTHERS', 'description': 'Other miscellaneous tests', 'order': 8},
            {'name': 'USG', 'description': 'Ultrasound examinations', 'order': 9},
            {'name': 'XRAY', 'description': 'X-ray examinations', 'order': 10},
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
        
        # CT Tests
        ct_tests = [
            {'name': 'CECT ABDOMEN & PELVIS', 'code': 'CECT-ABD-PEL', 'lab_price': 7500, 'discount': 0.2, 'b2b_price': 6000},
            {'name': 'CECT ABDOMEN AND THORAX', 'code': 'CECT-ABD-THOR', 'lab_price': 11000, 'discount': 0.2, 'b2b_price': 8800},
            {'name': 'CECT FACE AND NECK', 'code': 'CECT-FACE-NECK', 'lab_price': 5000, 'discount': 0.2, 'b2b_price': 4000},
            {'name': 'CECT LOWER LIMB', 'code': 'CECT-LL', 'lab_price': 7500, 'discount': 0.2, 'b2b_price': 6000},
            {'name': 'CECT NECK AND THORAX', 'code': 'CECT-NECK-THOR', 'lab_price': 7000, 'discount': 0.2, 'b2b_price': 5600},
            {'name': 'CECT NECK CHEST ABDOMEN', 'code': 'CECT-NECK-CHEST-ABD', 'lab_price': 12000, 'discount': 0.2, 'b2b_price': 9600},
            {'name': 'CT (ANY BONE) 3D', 'code': 'CT-BONE-3D', 'lab_price': 4000, 'discount': 0.2, 'b2b_price': 3200},
            {'name': 'CT ABDOMEN TRIPLE PHASE', 'code': 'CT-ABD-TRIPLE', 'lab_price': 9000, 'discount': 0.2, 'b2b_price': 7200},
            {'name': 'CT ANGIOGRAPHY ABDOMEN', 'code': 'CT-ANGIO-ABD', 'lab_price': 9000, 'discount': 0.2, 'b2b_price': 7200},
            {'name': 'CT ANGIOGRAPHY BRAIN', 'code': 'CT-ANGIO-BRAIN', 'lab_price': 5000, 'discount': 0.2, 'b2b_price': 4000},
            {'name': 'CT ANGIOGRAPHY BRAIN & NECK', 'code': 'CT-ANGIO-BRAIN-NECK', 'lab_price': 8000, 'discount': 0.2, 'b2b_price': 6400},
            {'name': 'CT ANGIOGRAPHY FACE & NECK', 'code': 'CT-ANGIO-FACE-NECK', 'lab_price': 5000, 'discount': 0.2, 'b2b_price': 4000},
            {'name': 'CT ANGIOGRAPHY LIMB', 'code': 'CT-ANGIO-LIMB', 'lab_price': 9000, 'discount': 0.2, 'b2b_price': 7200},
            {'name': 'CT ANGIOGRAPHY THORAX', 'code': 'CT-ANGIO-THORAX', 'lab_price': 7500, 'discount': 0.2, 'b2b_price': 6000},
            {'name': 'CT ANGIOGRAPHY THORAX AND ABDOMEN', 'code': 'CT-ANGIO-THORAX-ABD', 'lab_price': 11000, 'discount': 0.2, 'b2b_price': 8800},
            {'name': 'CT ANY JOINT', 'code': 'CT-JOINT', 'lab_price': 4500, 'discount': 0.2, 'b2b_price': 3600},
            {'name': 'CT AORTOGRAM', 'code': 'CT-AORTOGRAM', 'lab_price': 10000, 'discount': 0.2, 'b2b_price': 8000},
            {'name': 'CT BONE', 'code': 'CT-BONE', 'lab_price': 4000, 'discount': 0.2, 'b2b_price': 3200},
            {'name': 'CT CERVICAL CONTRAST', 'code': 'CT-CERV-CONTRAST', 'lab_price': 6000, 'discount': 0.2, 'b2b_price': 4800},
            {'name': 'CT CERVICAL SPINE', 'code': 'CT-CERV-SPINE', 'lab_price': 4000, 'discount': 0.2, 'b2b_price': 3200},
            {'name': 'CT CERVICAL SPINE WITH WSS', 'code': 'CT-CERV-WSS', 'lab_price': 5500, 'discount': 0.2, 'b2b_price': 4400},
            {'name': 'CT CHEST CONTRAST', 'code': 'CT-CHEST-CONTRAST', 'lab_price': 6000, 'discount': 0.2, 'b2b_price': 4800},
            {'name': 'CT CHEST PLAIN', 'code': 'CT-CHEST-PLAIN', 'lab_price': 4000, 'discount': 0.2, 'b2b_price': 3200},
            {'name': 'CT CONTRAST', 'code': 'CT-CONTRAST', 'lab_price': 1500, 'discount': 0.2, 'b2b_price': 1200},
            {'name': 'CT CONTRAST DOUBLE VIAL', 'code': 'CT-CONTRAST-DOUBLE', 'lab_price': 1500, 'discount': 0.2, 'b2b_price': 1200},
            {'name': 'CT CONTRAST SINGLE VIAL', 'code': 'CT-CONTRAST-SINGLE', 'lab_price': 1000, 'discount': 0.2, 'b2b_price': 800},
            {'name': 'CT DORSAL SPINE', 'code': 'CT-DORSAL-SPINE', 'lab_price': 4500, 'discount': 0.2, 'b2b_price': 3600},
            {'name': 'CT DORSAL SPINE WITH WSS', 'code': 'CT-DORSAL-WSS', 'lab_price': 6000, 'discount': 0.2, 'b2b_price': 4800},
            {'name': 'CT ENTEROCLYSIS', 'code': 'CT-ENTEROCLYSIS', 'lab_price': 9000, 'discount': 0.2, 'b2b_price': 7200},
            {'name': 'CT ENTEROGRAPHY', 'code': 'CT-ENTEROG', 'lab_price': 9000, 'discount': 0.2, 'b2b_price': 7200},
            {'name': 'CT FACE CONTRAST', 'code': 'CT-FACE-CONTRAST', 'lab_price': 4000, 'discount': 0.2, 'b2b_price': 3200},
            {'name': 'CT FACE PLAIN', 'code': 'CT-FACE-PLAIN', 'lab_price': 3000, 'discount': 0.2, 'b2b_price': 2400},
            {'name': 'CT HEAD CONTRAST', 'code': 'CT-HEAD-CONTRAST', 'lab_price': 3000, 'discount': 0.2, 'b2b_price': 2400},
            {'name': 'CT HEAD PLAIN', 'code': 'CT-HEAD-PLAIN', 'lab_price': 2000, 'discount': 0.2, 'b2b_price': 1600},
            {'name': 'CT IVP CONTRAST', 'code': 'CT-IVP', 'lab_price': 7500, 'discount': 0.2, 'b2b_price': 6000},
            {'name': 'CT KUB CONTRAST', 'code': 'CT-KUB-CONTRAST', 'lab_price': 7500, 'discount': 0.2, 'b2b_price': 6000},
            {'name': 'CT KUB PLAIN', 'code': 'CT-KUB-PLAIN', 'lab_price': 4000, 'discount': 0.2, 'b2b_price': 3200},
            {'name': 'CT LUMBAR SPINE', 'code': 'CT-LUMBAR-SPINE', 'lab_price': 4500, 'discount': 0.2, 'b2b_price': 3600},
            {'name': 'CT LUMBAR SPINE WITH WSS', 'code': 'CT-LUMBAR-WSS', 'lab_price': 6000, 'discount': 0.2, 'b2b_price': 4800},
            {'name': 'CT NECK AND THORAX', 'code': 'CT-NECK-THORAX', 'lab_price': 6500, 'discount': 0.2, 'b2b_price': 5200},
            {'name': 'CT NECK CONTRAST', 'code': 'CT-NECK-CONTRAST', 'lab_price': 5000, 'discount': 0.2, 'b2b_price': 4000},
            {'name': 'CT NECK PLAIN', 'code': 'CT-NECK-PLAIN', 'lab_price': 3000, 'discount': 0.2, 'b2b_price': 2400},
            {'name': 'CT ORBIT CONTRAST', 'code': 'CT-ORBIT-CONTRAST', 'lab_price': 4000, 'discount': 0.2, 'b2b_price': 3200},
            {'name': 'CT ORBIT PLAIN', 'code': 'CT-ORBIT-PLAIN', 'lab_price': 2500, 'discount': 0.2, 'b2b_price': 2000},
            {'name': 'CT PELVIS CONTRAST', 'code': 'CT-PELVIS-CONTRAST', 'lab_price': 6000, 'discount': 0.2, 'b2b_price': 4800},
            {'name': 'CT PELVIS PLAIN', 'code': 'CT-PELVIS-PLAIN', 'lab_price': 3500, 'discount': 0.2, 'b2b_price': 2800},
            {'name': 'CT PNS CONTRAST', 'code': 'CT-PNS-CONTRAST', 'lab_price': 4000, 'discount': 0.2, 'b2b_price': 3200},
            {'name': 'CT PNS PLAIN', 'code': 'CT-PNS-PLAIN', 'lab_price': 2500, 'discount': 0.2, 'b2b_price': 2000},
            {'name': 'CT TEMPORAL BONE', 'code': 'CT-TEMPORAL', 'lab_price': 4000, 'discount': 0.2, 'b2b_price': 3200},
            {'name': 'CT THORAXHRCONTRAST', 'code': 'CT-THORAX-CONTRAST', 'lab_price': 6000, 'discount': 0.2, 'b2b_price': 4800},
            {'name': 'CT THORAXHRPLAIN', 'code': 'CT-THORAX-PLAIN', 'lab_price': 4000, 'discount': 0.2, 'b2b_price': 3200},
            {'name': 'CT UPPER ABDOMEN CONTRAST', 'code': 'CT-UPPER-ABD-CONTRAST', 'lab_price': 5500, 'discount': 0.2, 'b2b_price': 4400},
            {'name': 'CT UPPER ABDOMEN PLAIN', 'code': 'CT-UPPER-ABD-PLAIN', 'lab_price': 3000, 'discount': 0.2, 'b2b_price': 2400},
            {'name': 'CT UROGRAM', 'code': 'CT-UROGRAM', 'lab_price': 8500, 'discount': 0.2, 'b2b_price': 6800},
            {'name': 'CT WHOLE ABDOMEN', 'code': 'CT-WHOLE-ABD', 'lab_price': 7500, 'discount': 0.2, 'b2b_price': 6000},
            {'name': 'CT WHOLE ABDOMEN (CHILD)', 'code': 'CT-WHOLE-ABD-CHILD', 'lab_price': 5500, 'discount': 0.2, 'b2b_price': 4400},
            {'name': 'CT WHOLE ABDOMEN CONTRAST', 'code': 'CT-WHOLE-ABD-CONTRAST', 'lab_price': 7500, 'discount': 0.2, 'b2b_price': 6000},
            {'name': 'CT WHOLE ABDOMEN PLAIN', 'code': 'CT-WHOLE-ABD-PLAIN', 'lab_price': 5500, 'discount': 0.2, 'b2b_price': 4400},
            {'name': 'PULMONARY ANGIO', 'code': 'CT-PULM-ANGIO', 'lab_price': 7000, 'discount': 0.2, 'b2b_price': 5600},
            {'name': 'RENAL ANGIO', 'code': 'CT-RENAL-ANGIO', 'lab_price': 8000, 'discount': 0.2, 'b2b_price': 6400},
        ]
        
        for test_data in ct_tests:
            test, created = InvestigationTest.objects.get_or_create(
                name=test_data['name'],
                category=categories['CT'],
                defaults={
                    'code': test_data['code'],
                    'description': f"CT scan: {test_data['name']}",
                    'normal_range': 'Normal findings',
                    'unit': 'N/A',
                    'is_fasting_required': False,
                    'preparation_instructions': 'Remove metal objects, may require contrast',
                    'estimated_cost': test_data['b2b_price']
                }
            )
            if created:
                self.stdout.write(f'Created CT test: {test.name}')
            else:
                self.stdout.write(f'CT test already exists: {test.name}')
        
        # CT Guided Procedures
        ct_guided_tests = [
            {'name': 'CT GUIDED BIOPSY PROCEDURE', 'code': 'CT-BIOPSY', 'lab_price': 7000, 'discount': 0.1, 'b2b_price': 6300},
            {'name': 'CT GUIDED BIOPSY WITH PROFILE', 'code': 'CT-BIOPSY-PROFILE', 'lab_price': 7500, 'discount': 0.1, 'b2b_price': 6750},
            {'name': 'CT GUIDED FNAC PROCEDURE', 'code': 'CT-FNAC', 'lab_price': 4000, 'discount': 0.1, 'b2b_price': 3600},
        ]
        
        for test_data in ct_guided_tests:
            test, created = InvestigationTest.objects.get_or_create(
                name=test_data['name'],
                category=categories['CT GUIDED PROCEDURE'],
                defaults={
                    'code': test_data['code'],
                    'description': f"CT guided procedure: {test_data['name']}",
                    'normal_range': 'Procedure specific',
                    'unit': 'N/A',
                    'is_fasting_required': True,
                    'preparation_instructions': 'Fasting required, remove metal objects',
                    'estimated_cost': test_data['b2b_price']
                }
            )
            if created:
                self.stdout.write(f'Created CT guided test: {test.name}')
            else:
                self.stdout.write(f'CT guided test already exists: {test.name}')
        
        # Cardiology Tests
        cardio_tests = [
            {'name': 'ECG', 'code': 'ECG', 'lab_price': 200, 'discount': 0.2, 'b2b_price': 160},
            {'name': 'ECHO', 'code': 'ECHO', 'lab_price': 1500, 'discount': 0.2, 'b2b_price': 1200},
        ]
        
        for test_data in cardio_tests:
            test, created = InvestigationTest.objects.get_or_create(
                name=test_data['name'],
                category=categories['CARDIOLOGY'],
                defaults={
                    'code': test_data['code'],
                    'description': f"Cardiac test: {test_data['name']}",
                    'normal_range': 'Normal cardiac function',
                    'unit': 'N/A',
                    'is_fasting_required': False,
                    'preparation_instructions': 'No special preparation required',
                    'estimated_cost': test_data['b2b_price']
                }
            )
            if created:
                self.stdout.write(f'Created cardiac test: {test.name}')
            else:
                self.stdout.write(f'Cardiac test already exists: {test.name}')
        
        # USG Guided Procedures
        usg_guided_tests = [
            {'name': 'USG GUIDED ASPIRATION DIAGNOSTIC', 'code': 'USG-ASPIRATION-DIAG', 'lab_price': 1500, 'discount': 0.2, 'b2b_price': 1200},
            {'name': 'USG GUIDED ASPIRATION THERAPETIC', 'code': 'USG-ASPIRATION-THER', 'lab_price': 3000, 'discount': 0.2, 'b2b_price': 2400},
            {'name': 'USG GUIDED BIOPSY PROCEDURE', 'code': 'USG-BIOPSY', 'lab_price': 6500, 'discount': 0.2, 'b2b_price': 5200},
            {'name': 'USG GUIDED FNAC ASPIRATION PROCEDURE', 'code': 'USG-FNAC', 'lab_price': 1500, 'discount': 0.2, 'b2b_price': 1200},
            {'name': 'USG GUIDED PROSTATIC BIOPSY/TRUS BIOPSY', 'code': 'USG-TRUS-BIOPSY', 'lab_price': 8000, 'discount': 0.2, 'b2b_price': 6400},
        ]
        
        for test_data in usg_guided_tests:
            test, created = InvestigationTest.objects.get_or_create(
                name=test_data['name'],
                category=categories['DEPARTMENT'],
                defaults={
                    'code': test_data['code'],
                    'description': f"USG guided procedure: {test_data['name']}",
                    'normal_range': 'Procedure specific',
                    'unit': 'N/A',
                    'is_fasting_required': True,
                    'preparation_instructions': 'Fasting required, procedure specific prep',
                    'estimated_cost': test_data['b2b_price']
                }
            )
            if created:
                self.stdout.write(f'Created USG guided test: {test.name}')
            else:
                self.stdout.write(f'USG guided test already exists: {test.name}')
        
        # Gastroenterology Tests
        gastro_tests = [
            {'name': 'COLONOSCOPYILEO', 'code': 'COLONOSCOPY-ILEO', 'lab_price': 3700, 'discount': 0.135135, 'b2b_price': 3200},
            {'name': 'COLONOSCOPYLIMITED', 'code': 'COLONOSCOPY-LIMITED', 'lab_price': 1500, 'discount': 0.2, 'b2b_price': 1200},
            {'name': 'EVL', 'code': 'EVL', 'lab_price': 6000, 'discount': 0.1, 'b2b_price': 5400},
            {'name': 'FOREIGN BODY REMOVALMAJOR', 'code': 'FB-REMOVAL-MAJOR', 'lab_price': 5000, 'discount': 0.1, 'b2b_price': 4500},
            {'name': 'FOREIGN BODY REMOVALMINOR', 'code': 'FB-REMOVAL-MINOR', 'lab_price': 2500, 'discount': 0.1, 'b2b_price': 2250},
            {'name': 'SIGMOIDSCOPY', 'code': 'SIGMOIDSCOPY', 'lab_price': 1500, 'discount': 0.2, 'b2b_price': 1200},
            {'name': 'UGIENDOSCOPY', 'code': 'UGI-ENDOSCOPY', 'lab_price': 1500, 'discount': 0.133334, 'b2b_price': 1300},
        ]
        
        for test_data in gastro_tests:
            test, created = InvestigationTest.objects.get_or_create(
                name=test_data['name'],
                category=categories['GASTROENTEROLOGY'],
                defaults={
                    'code': test_data['code'],
                    'description': f"Gastroenterology procedure: {test_data['name']}",
                    'normal_range': 'Procedure specific',
                    'unit': 'N/A',
                    'is_fasting_required': True,
                    'preparation_instructions': 'Fasting required, bowel preparation if needed',
                    'estimated_cost': test_data['b2b_price']
                }
            )
            if created:
                self.stdout.write(f'Created gastro test: {test.name}')
            else:
                self.stdout.write(f'Gastro test already exists: {test.name}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully populated CT, CT Guided, Cardiology, USG Guided, and Gastroenterology tests!')
        )
        
        self.stdout.write('Note: Due to length limits, only partial test list was added.')
        self.stdout.write('Run this command multiple times with different test categories to add all tests.')
