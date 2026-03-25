from django.core.management.base import BaseCommand
from prescriptions.models import InvestigationCategory, InvestigationTest


class Command(BaseCommand):
    help = 'Populate database with remaining investigation tests (MRI, USG, XRAY, etc.)'

    def handle(self, *args, **options):
        self.stdout.write('Creating remaining investigation tests...')
        
        # Get existing categories
        try:
            mri_category = InvestigationCategory.objects.get(name='MRI')
            usg_category = InvestigationCategory.objects.get(name='USG')
            xray_category = InvestigationCategory.objects.get(name='XRAY')
            mammo_category = InvestigationCategory.objects.get(name='MAMMOGRAPHY')
            others_category = InvestigationCategory.objects.get(name='OTHERS')
        except InvestigationCategory.DoesNotExist:
            self.stdout.write(self.style.ERROR('Required categories not found. Run populate_complete_investigations first.'))
            return
        
        # MRI Tests
        mri_tests = [
            {'name': 'CARDIAC MRI', 'code': 'MRI-CARDIAC', 'lab_price': 11000, 'discount': 0.2, 'b2b_price': 8800},
            {'name': 'MP MRI PROSTRATE (CONTRAST)', 'code': 'MRI-PROSTATE', 'lab_price': 9000, 'discount': 0.2, 'b2b_price': 7200},
            {'name': 'MRA', 'code': 'MRI-MRA', 'lab_price': 1500, 'discount': 0.2, 'b2b_price': 1200},
            {'name': 'MRCP', 'code': 'MRI-MRCP', 'lab_price': 7000, 'discount': 0.2, 'b2b_price': 5600},
            {'name': 'MRI ABDOMEN WITH MRCP', 'code': 'MRI-ABD-MRCP', 'lab_price': 8000, 'discount': 0.2, 'b2b_price': 6400},
            {'name': 'MRI ADDITIONAL SCREENING', 'code': 'MRI-ADD-SCREEN', 'lab_price': 3000, 'discount': 0.2, 'b2b_price': 2400},
            {'name': 'MRI ANGIO (CAROTID)', 'code': 'MRI-ANGIO-CAROTID', 'lab_price': 1500, 'discount': 0.2, 'b2b_price': 1200},
            {'name': 'MRI ANGIOGRAM/VENOGRAM/SPECTROSCOPY', 'code': 'MRI-ANGIO-VENO', 'lab_price': 9000, 'discount': 0.2, 'b2b_price': 7200},
            {'name': 'MRI ANKLE JOINT', 'code': 'MRI-ANKLE', 'lab_price': 6500, 'discount': 0.2, 'b2b_price': 5200},
            {'name': 'MRI BILATERAL KNEE', 'code': 'MRI-BILAT-KNEE', 'lab_price': 11000, 'discount': 0.2, 'b2b_price': 8800},
            {'name': 'MRI BILATERAL SHOULDER', 'code': 'MRI-BILAT-SHOULDER', 'lab_price': 12000, 'discount': 0.2, 'b2b_price': 9600},
            {'name': 'MRI BILATERAL SI JOINT', 'code': 'MRI-BILAT-SI', 'lab_price': 7500, 'discount': 0.2, 'b2b_price': 6000},
            {'name': 'MRI BRACHIAL PLEXUS COMPLETE', 'code': 'MRI-BRACHIAL-COMPLETE', 'lab_price': 6500, 'discount': 0.2, 'b2b_price': 5200},
            {'name': 'MRI BRACHIAL PLEXUS SCREENING', 'code': 'MRI-BRACHIAL-SCREEN', 'lab_price': 6500, 'discount': 0.2, 'b2b_price': 5200},
            {'name': 'MRI BRAIN ANGIO', 'code': 'MRI-BRAIN-ANGIO', 'lab_price': 8000, 'discount': 0.2, 'b2b_price': 6400},
            {'name': 'MRI BRAIN & PERFUSION & SPECTRO', 'code': 'MRI-BRAIN-PERF-SPECTRO', 'lab_price': 10500, 'discount': 0.2, 'b2b_price': 8400},
            {'name': 'MRI BRAIN AND MASTOID', 'code': 'MRI-BRAIN-MASTOID', 'lab_price': 8000, 'discount': 0.2, 'b2b_price': 6400},
            {'name': 'MRI BRAIN AND ORBIT', 'code': 'MRI-BRAIN-ORBIT', 'lab_price': 8000, 'discount': 0.2, 'b2b_price': 6400},
            {'name': 'MRI BRAIN AND PNS', 'code': 'MRI-BRAIN-PNS', 'lab_price': 8000, 'discount': 0.2, 'b2b_price': 6400},
            {'name': 'MRI BRAIN WITH ANGIO (BRAIN & NECK VESSELS)', 'code': 'MRI-BRAIN-ANGIO-NECK', 'lab_price': 9000, 'discount': 0.2, 'b2b_price': 7200},
            {'name': 'MRI BRAIN WITH MRA AND MRV', 'code': 'MRI-BRAIN-MRA-MRV', 'lab_price': 8000, 'discount': 0.2, 'b2b_price': 6400},
            {'name': 'MRI BRAIN WITH SCREENING OF CERVICAL SPINE', 'code': 'MRI-BRAIN-CERV-SCREEN', 'lab_price': 7000, 'discount': 0.2, 'b2b_price': 5600},
            {'name': 'MRI BRAIN WITH VENOGRAM', 'code': 'MRI-BRAIN-VENOGRAM', 'lab_price': 8000, 'discount': 0.2, 'b2b_price': 6400},
            {'name': 'MRI BRAIN WITH WHOLE SPINE SCREENING', 'code': 'MRI-BRAIN-SPINE-SCREEN', 'lab_price': 7000, 'discount': 0.2, 'b2b_price': 5600},
            {'name': 'MRI BREAST (CONTRAST)', 'code': 'MRI-BREAST-CONTRAST', 'lab_price': 9000, 'discount': 0.2, 'b2b_price': 7200},
            {'name': 'MRI CERVICAL SPINE', 'code': 'MRI-CERV-SPINE', 'lab_price': 6500, 'discount': 0.2, 'b2b_price': 5200},
            {'name': 'MRI CERVICAL SPINE WITH WSS', 'code': 'MRI-CERV-WSS', 'lab_price': 7000, 'discount': 0.2, 'b2b_price': 5600},
            {'name': 'MRI CISTERNOGRAPHY', 'code': 'MRI-CISTERNOGRAPHY', 'lab_price': 8000, 'discount': 0.2, 'b2b_price': 6400},
            {'name': 'MRI CONTRAST', 'code': 'MRI-CONTRAST', 'lab_price': 2500, 'discount': 0.2, 'b2b_price': 2000},
            {'name': 'MRI DORSAL SPINE', 'code': 'MRI-DORSAL-SPINE', 'lab_price': 6500, 'discount': 0.2, 'b2b_price': 5200},
            {'name': 'MRI DORSAL SPINE WITH WSS', 'code': 'MRI-DORSAL-WSS', 'lab_price': 7000, 'discount': 0.2, 'b2b_price': 5600},
            {'name': 'MRI DOUBLE PART', 'code': 'MRI-DOUBLE-PART', 'lab_price': 11000, 'discount': 0.2, 'b2b_price': 8800},
            {'name': 'MRI ENTEROGRAPHY', 'code': 'MRI-ENTEROG', 'lab_price': 6500, 'discount': 0.2, 'b2b_price': 5200},
            {'name': 'MRI FACE AND NECK', 'code': 'MRI-FACE-NECK', 'lab_price': 6500, 'discount': 0.2, 'b2b_price': 5200},
            {'name': 'MRI FISTULOGRAM', 'code': 'MRI-FISTULOGRAM', 'lab_price': 6500, 'discount': 0.2, 'b2b_price': 5200},
            {'name': 'MRI HAND', 'code': 'MRI-HAND', 'lab_price': 6500, 'discount': 0.2, 'b2b_price': 5200},
            {'name': 'MRI HEAD (BRAIN)', 'code': 'MRI-HEAD-BRAIN', 'lab_price': 6500, 'discount': 0.2, 'b2b_price': 5200},
            {'name': 'MRI HEAD (PITUITARY)', 'code': 'MRI-HEAD-PITUITARY', 'lab_price': 6500, 'discount': 0.2, 'b2b_price': 5200},
            {'name': 'MRI HIP AND SI JOINT SCREENING', 'code': 'MRI-HIP-SI-SCREEN', 'lab_price': 9000, 'discount': 0.2, 'b2b_price': 7200},
            {'name': 'MRI HIP JOINT', 'code': 'MRI-HIP', 'lab_price': 8000, 'discount': 0.2, 'b2b_price': 6400},
            {'name': 'MRI KNEE JOINT', 'code': 'MRI-KNEE', 'lab_price': 6500, 'discount': 0.2, 'b2b_price': 5200},
            {'name': 'MRI LIVER MULTI PHASE', 'code': 'MRI-LIVER-MULTI', 'lab_price': 6500, 'discount': 0.2, 'b2b_price': 5200},
            {'name': 'MRI LOWER LIMB ANGIOGRAM', 'code': 'MRI-LL-ANGIO', 'lab_price': 8000, 'discount': 0.2, 'b2b_price': 6400},
            {'name': 'MRI LS PLEXUS SCREENING', 'code': 'MRI-LS-PLEXUS', 'lab_price': 6500, 'discount': 0.2, 'b2b_price': 5200},
            {'name': 'MRI LS SPINE', 'code': 'MRI-LS-SPINE', 'lab_price': 6500, 'discount': 0.2, 'b2b_price': 5200},
            {'name': 'MRI LS SPINE WITH SCREENING OF SI JOINT', 'code': 'MRI-LS-SI-SCREEN', 'lab_price': 7500, 'discount': 0.2, 'b2b_price': 6000},
            {'name': 'MRI LS SPINE WITH SCREENING OF WHOLE SPINE', 'code': 'MRI-LS-WHOLE-SPINE', 'lab_price': 7000, 'discount': 0.2, 'b2b_price': 5600},
            {'name': 'MRI LS SPINE WITH SCREENING OF WHOLE SPINE & SI JOINT', 'code': 'MRI-LS-WHOLE-SPINE-SI', 'lab_price': 7500, 'discount': 0.2, 'b2b_price': 6000},
            {'name': 'MRI NECK', 'code': 'MRI-NECK', 'lab_price': 6500, 'discount': 0.2, 'b2b_price': 5200},
            {'name': 'MRI NECKANGIO', 'code': 'MRI-NECK-ANGIO', 'lab_price': 8000, 'discount': 0.2, 'b2b_price': 6400},
            {'name': 'MRI ORBITS AND PNS', 'code': 'MRI-ORBITS-PNS', 'lab_price': 6500, 'discount': 0.2, 'b2b_price': 5200},
            {'name': 'MRI PELVIS', 'code': 'MRI-PELVIS', 'lab_price': 6500, 'discount': 0.2, 'b2b_price': 5200},
            {'name': 'MRI PERFUSION', 'code': 'MRI-PERFUSION', 'lab_price': 2000, 'discount': 0.2, 'b2b_price': 1600},
            {'name': 'MRI PERINEUM WITH FISTULOGRAM', 'code': 'MRI-PERINEUM-FISTULO', 'lab_price': 6500, 'discount': 0.2, 'b2b_price': 5200},
            {'name': 'MRI RENAL ANGIOGRAPHY', 'code': 'MRI-RENAL-ANGIO', 'lab_price': 7000, 'discount': 0.2, 'b2b_price': 5600},
            {'name': 'MRI SCREENING (STROKE)', 'code': 'MRI-SCREEN-STROKE', 'lab_price': 3500, 'discount': 0.2, 'b2b_price': 2800},
            {'name': 'MRI SCREENING BRAIN', 'code': 'MRI-SCREEN-BRAIN', 'lab_price': 3000, 'discount': 0.2, 'b2b_price': 2400},
            {'name': 'MRI SHOULDER JOINT', 'code': 'MRI-SHOULDER', 'lab_price': 6500, 'discount': 0.2, 'b2b_price': 5200},
            {'name': 'MRI SI JOINT WITH WSS', 'code': 'MRI-SI-WSS', 'lab_price': 7000, 'discount': 0.2, 'b2b_price': 5600},
            {'name': 'MRI SINGLE JOINT SCREENING (ANY ONE)', 'code': 'MRI-SINGLE-JOINT', 'lab_price': 3000, 'discount': 0.2, 'b2b_price': 2400},
            {'name': 'MRI SINGLE STUDY', 'code': 'MRI-SINGLE-STUDY', 'lab_price': 6500, 'discount': 0.2, 'b2b_price': 5200},
            {'name': 'MRI SINOGRAM', 'code': 'MRI-SINOGRAM', 'lab_price': 6500, 'discount': 0.2, 'b2b_price': 5200},
            {'name': 'MRI SPECTROSCOPY (MRS)', 'code': 'MRI-SPECTROSCOPY', 'lab_price': 2000, 'discount': 0.2, 'b2b_price': 1600},
            {'name': 'MRI THORACIC SPINE', 'code': 'MRI-THORACIC-SPINE', 'lab_price': 6500, 'discount': 0.2, 'b2b_price': 5200},
            {'name': 'MRI THORACIC SPINE WITH WSS', 'code': 'MRI-THORACIC-WSS', 'lab_price': 7000, 'discount': 0.2, 'b2b_price': 5600},
            {'name': 'MRI TONGUE', 'code': 'MRI-TONGUE', 'lab_price': 6500, 'discount': 0.2, 'b2b_price': 5200},
            {'name': 'MRI TRIPLE PHASE', 'code': 'MRI-TRIPLE-PHASE', 'lab_price': 9000, 'discount': 0.2, 'b2b_price': 7200},
            {'name': 'MRI UPPER ABDOMEN', 'code': 'MRI-UPPER-ABD', 'lab_price': 6500, 'discount': 0.2, 'b2b_price': 5200},
            {'name': 'MRI UROGRAPHY', 'code': 'MRI-UROGRAPHY', 'lab_price': 7000, 'discount': 0.2, 'b2b_price': 5600},
            {'name': 'MRI WHOLE ABDOMEN', 'code': 'MRI-WHOLE-ABD', 'lab_price': 6500, 'discount': 0.2, 'b2b_price': 5200},
            {'name': 'MRI WHOLE BODY', 'code': 'MRI-WHOLE-BODY', 'lab_price': 15000, 'discount': 0.2, 'b2b_price': 12000},
            {'name': 'MRI WHOLE SPINE', 'code': 'MRI-WHOLE-SPINE', 'lab_price': 7000, 'discount': 0.2, 'b2b_price': 5600},
            {'name': 'MRI WRIST JOINT', 'code': 'MRI-WRIST', 'lab_price': 6500, 'discount': 0.2, 'b2b_price': 5200},
            {'name': 'MRV', 'code': 'MRI-MRV', 'lab_price': 1500, 'discount': 0.2, 'b2b_price': 1200},
        ]
        
        for test_data in mri_tests:
            test, created = InvestigationTest.objects.get_or_create(
                name=test_data['name'],
                category=mri_category,
                defaults={
                    'code': test_data['code'],
                    'description': f"MRI scan: {test_data['name']}",
                    'normal_range': 'Normal findings',
                    'unit': 'N/A',
                    'is_fasting_required': False,
                    'preparation_instructions': 'Remove all metal objects, may require contrast',
                    'estimated_cost': test_data['b2b_price']
                }
            )
            if created:
                self.stdout.write(f'Created MRI test: {test.name}')
            else:
                self.stdout.write(f'MRI test already exists: {test.name}')
        
        # Mammography Tests
        mammo_tests = [
            {'name': 'BOTH BREAST MAMMOGRAPHY', 'code': 'MAMMO-BOTH', 'lab_price': 2500, 'discount': 0.2, 'b2b_price': 2000},
            {'name': 'SINGLE BREAST MAMMOGRAPHY', 'code': 'MAMMO-SINGLE', 'lab_price': 1500, 'discount': 0.2, 'b2b_price': 1200},
        ]
        
        for test_data in mammo_tests:
            test, created = InvestigationTest.objects.get_or_create(
                name=test_data['name'],
                category=mammo_category,
                defaults={
                    'code': test_data['code'],
                    'description': f"Mammography: {test_data['name']}",
                    'normal_range': 'Normal breast tissue',
                    'unit': 'N/A',
                    'is_fasting_required': False,
                    'preparation_instructions': 'No special preparation required',
                    'estimated_cost': test_data['b2b_price']
                }
            )
            if created:
                self.stdout.write(f'Created mammography test: {test.name}')
            else:
                self.stdout.write(f'Mammography test already exists: {test.name}')
        
        # Other Tests
        other_tests = [
            {'name': 'CD CHARGES', 'code': 'CD-CHARGES', 'lab_price': 200, 'discount': 0.1, 'b2b_price': 180},
            {'name': 'PFT1 (Pulmonary Function Test)', 'code': 'PFT1', 'lab_price': 450, 'discount': 0.2, 'b2b_price': 360},
            {'name': 'PFT2 (Pulmonary Function Test)', 'code': 'PFT2', 'lab_price': 750, 'discount': 0.2, 'b2b_price': 600},
        ]
        
        for test_data in other_tests:
            test, created = InvestigationTest.objects.get_or_create(
                name=test_data['name'],
                category=others_category,
                defaults={
                    'code': test_data['code'],
                    'description': f"Other test: {test_data['name']}",
                    'normal_range': 'Test specific',
                    'unit': 'N/A',
                    'is_fasting_required': False,
                    'preparation_instructions': 'No special preparation required',
                    'estimated_cost': test_data['b2b_price']
                }
            )
            if created:
                self.stdout.write(f'Created other test: {test.name}')
            else:
                self.stdout.write(f'Other test already exists: {test.name}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully populated MRI, Mammography, and Other tests!')
        )
        
        self.stdout.write('Note: USG and XRAY tests will be added in the next command due to length limits.')
