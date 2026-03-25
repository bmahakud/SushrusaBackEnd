from django.core.management.base import BaseCommand
from prescriptions.models import InvestigationCategory, InvestigationTest


class Command(BaseCommand):
    help = 'Populate database with USG and XRAY investigation tests'

    def handle(self, *args, **options):
        self.stdout.write('Creating USG and XRAY investigation tests...')
        
        # Get existing categories
        try:
            usg_category = InvestigationCategory.objects.get(name='USG')
            xray_category = InvestigationCategory.objects.get(name='XRAY')
        except InvestigationCategory.DoesNotExist:
            self.stdout.write(self.style.ERROR('Required categories not found. Run populate_complete_investigations first.'))
            return
        
        # USG Tests
        usg_tests = [
            {'name': 'CAROTID DOPPLER', 'code': 'USG-CAROTID-DOPPLER', 'lab_price': 1500, 'discount': 0.2, 'b2b_price': 1200},
            {'name': 'DOPPLER UPPER LIMB', 'code': 'USG-DOPPLER-UL', 'lab_price': 2000, 'discount': 0.2, 'b2b_price': 1600},
            {'name': 'DOPPLER (PREGNANCY/OBSTETRICS)', 'code': 'USG-DOPPLER-OBST', 'lab_price': 1800, 'discount': 0.2, 'b2b_price': 1440},
            {'name': 'DOPPLER (PREGNANCY/OBSTETRICSTWINS)', 'code': 'USG-DOPPLER-TWINS', 'lab_price': 3000, 'discount': 0.2, 'b2b_price': 2400},
            {'name': 'DOPPLER ARTERY + VEIN B/L LL', 'code': 'USG-DOPPLER-ARTERY-VEIN-LL', 'lab_price': 4000, 'discount': 0.2, 'b2b_price': 3200},
            {'name': 'DOPPLER BILATERAL UPPER LIMBS', 'code': 'USG-DOPPLER-BILAT-UL', 'lab_price': 3200, 'discount': 0.2, 'b2b_price': 2560},
            {'name': 'DOPPLER LOWER LIMB ARTERIAL + VENOUS', 'code': 'USG-DOPPLER-LL-ARTERY-VENOUS', 'lab_price': 3000, 'discount': 0.2, 'b2b_price': 2400},
            {'name': 'DOPPLER PERIPHERAL ARTERY / VEINS', 'code': 'USG-DOPPLER-PERIPHERAL', 'lab_price': 1500, 'discount': 0.2, 'b2b_price': 1200},
            {'name': 'DOPPLER PORTAL VENOUS', 'code': 'USG-DOPPLER-PORTAL', 'lab_price': 1500, 'discount': 0.2, 'b2b_price': 1200},
            {'name': 'DOPPLER SCREENING DVT', 'code': 'USG-DOPPLER-DVT', 'lab_price': 1500, 'discount': 0.2, 'b2b_price': 1200},
            {'name': 'DOPPLER STUDY OF SMALL PART SCROTUM', 'code': 'USG-DOPPLER-SCROTUM', 'lab_price': 1000, 'discount': 0.2, 'b2b_price': 800},
            {'name': 'DOPPLER STUDY OF SMALL PART SWELLING', 'code': 'USG-DOPPLER-SWELLING', 'lab_price': 1000, 'discount': 0.2, 'b2b_price': 800},
            {'name': 'DOPPLER STUDY OF SMALL PART THYROID', 'code': 'USG-DOPPLER-THYROID', 'lab_price': 1000, 'discount': 0.2, 'b2b_price': 800},
            {'name': 'DOPPLER STUDY RENAL ARTERY', 'code': 'USG-DOPPLER-RENAL-ARTERY', 'lab_price': 2000, 'discount': 0.2, 'b2b_price': 1600},
            {'name': 'DOPPLER STUDY SPLENOPORTALAXIS', 'code': 'USG-DOPPLER-SPLENOPORTAL', 'lab_price': 2000, 'discount': 0.2, 'b2b_price': 1600},
            {'name': 'ELASTOGRAPHY', 'code': 'USG-ELASTOGRAPHY', 'lab_price': 1000, 'discount': 0.2, 'b2b_price': 800},
            {'name': 'PENILE DOPPLER', 'code': 'USG-PENILE-DOPPLER', 'lab_price': 1500, 'discount': 0.2, 'b2b_price': 1200},
            {'name': 'REVIEW USG', 'code': 'USG-REVIEW', 'lab_price': 400, 'discount': 0.2, 'b2b_price': 320},
            {'name': 'USG ABDOMEN & KUB (FEMALE)', 'code': 'USG-ABD-KUB-FEMALE', 'lab_price': 1000, 'discount': 0.2, 'b2b_price': 800},
            {'name': 'USG ABDOMEN AND PELVIS', 'code': 'USG-ABD-PELVIS', 'lab_price': 1000, 'discount': 0.2, 'b2b_price': 800},
            {'name': 'USG BREAST', 'code': 'USG-BREAST', 'lab_price': 1000, 'discount': 0.2, 'b2b_price': 800},
            {'name': 'USG CALF', 'code': 'USG-CALF', 'lab_price': 1000, 'discount': 0.2, 'b2b_price': 800},
            {'name': 'USG CHEST', 'code': 'USG-CHEST', 'lab_price': 800, 'discount': 0.2, 'b2b_price': 640},
            {'name': 'USG FETAL WELL BEING', 'code': 'USG-FWB', 'lab_price': 1000, 'discount': 0.2, 'b2b_price': 800},
            {'name': 'USG FETAL WELL BEING(TWIN)', 'code': 'USG-FWB-TWIN', 'lab_price': 1500, 'discount': 0.2, 'b2b_price': 1200},
            {'name': 'USG FOLLICULAR STUDY', 'code': 'USG-FOLLICULAR', 'lab_price': 1500, 'discount': 0.2, 'b2b_price': 1200},
            {'name': 'USG FWB', 'code': 'USG-FWB-BASIC', 'lab_price': 1100, 'discount': 0.2, 'b2b_price': 880},
            {'name': 'USG FWB (BIOPHYSICAL PROFILE)', 'code': 'USG-FWB-BPP', 'lab_price': 1500, 'discount': 0.2, 'b2b_price': 1200},
            {'name': 'USG FWB (EARLY PREGNANCY)', 'code': 'USG-FWB-EARLY', 'lab_price': 900, 'discount': 0.2, 'b2b_price': 720},
            {'name': 'USG FWB WITH ABD', 'code': 'USG-FWB-ABD', 'lab_price': 1500, 'discount': 0.2, 'b2b_price': 1200},
            {'name': 'USG KNEE SINGLE', 'code': 'USG-KNEE-SINGLE', 'lab_price': 700, 'discount': 0.2, 'b2b_price': 560},
            {'name': 'USG KUB', 'code': 'USG-KUB', 'lab_price': 800, 'discount': 0.2, 'b2b_price': 640},
            {'name': 'USG MUSCULOSKELETAL', 'code': 'USG-MSK', 'lab_price': 700, 'discount': 0.2, 'b2b_price': 560},
            {'name': 'USG NECK', 'code': 'USG-NECK', 'lab_price': 800, 'discount': 0.2, 'b2b_price': 640},
            {'name': 'USG NT SCAN', 'code': 'USG-NT-SCAN', 'lab_price': 1500, 'discount': 0.2, 'b2b_price': 1200},
            {'name': 'USG NT SCAN (TWIN)', 'code': 'USG-NT-SCAN-TWIN', 'lab_price': 2000, 'discount': 0.2, 'b2b_price': 1600},
            {'name': 'USG ORBIT ( B SCAN)', 'code': 'USG-ORBIT-BSCAN', 'lab_price': 800, 'discount': 0.2, 'b2b_price': 640},
            {'name': 'USG PELVIS', 'code': 'USG-PELVIS', 'lab_price': 800, 'discount': 0.2, 'b2b_price': 640},
            {'name': 'USG SCROTUM', 'code': 'USG-SCROTUM', 'lab_price': 1000, 'discount': 0.2, 'b2b_price': 800},
            {'name': 'USG SMALL PART DOPPLER', 'code': 'USG-SMALL-PART-DOPPLER', 'lab_price': 1000, 'discount': 0.2, 'b2b_price': 800},
            {'name': 'USG SMALL PARTS', 'code': 'USG-SMALL-PARTS', 'lab_price': 800, 'discount': 0.2, 'b2b_price': 640},
            {'name': 'USG TARGET SCAN/ANOMALY/TIFA', 'code': 'USG-TARGET-SCAN', 'lab_price': 1800, 'discount': 0.2, 'b2b_price': 1440},
            {'name': 'USG TARGET SCAN/ANOMALY/TIFA (TWIN)', 'code': 'USG-TARGET-SCAN-TWIN', 'lab_price': 3000, 'discount': 0.2, 'b2b_price': 2400},
            {'name': 'USG THIGH', 'code': 'USG-THIGH', 'lab_price': 1000, 'discount': 0.2, 'b2b_price': 800},
            {'name': 'USG THYROID', 'code': 'USG-THYROID', 'lab_price': 700, 'discount': 0.2, 'b2b_price': 560},
            {'name': 'USG THYROID GLAND', 'code': 'USG-THYROID-GLAND', 'lab_price': 1000, 'discount': 0.2, 'b2b_price': 800},
            {'name': 'USG TRANSCRANIAL', 'code': 'USG-TRANSCRANIAL', 'lab_price': 800, 'discount': 0.2, 'b2b_price': 640},
            {'name': 'USG TRUS', 'code': 'USG-TRUS', 'lab_price': 1200, 'discount': 0.2, 'b2b_price': 960},
            {'name': 'USG TVS', 'code': 'USG-TVS', 'lab_price': 1000, 'discount': 0.2, 'b2b_price': 800},
            {'name': 'USG WHOLE ABDOMEN', 'code': 'USG-WHOLE-ABD', 'lab_price': 1000, 'discount': 0.2, 'b2b_price': 800},
            {'name': 'USG WHOLE ABDOMEN (FEMALE)', 'code': 'USG-WHOLE-ABD-FEMALE', 'lab_price': 1000, 'discount': 0.2, 'b2b_price': 800},
            {'name': 'USG GUIDED ASPIRATION THERAPETIC (PIG TAILING)', 'code': 'USG-GUIDED-PIGTAIL', 'lab_price': 11000, 'discount': 0.2, 'b2b_price': 8800},
        ]
        
        for test_data in usg_tests:
            test, created = InvestigationTest.objects.get_or_create(
                name=test_data['name'],
                category=usg_category,
                defaults={
                    'code': test_data['code'],
                    'description': f"Ultrasound: {test_data['name']}",
                    'normal_range': 'Normal findings',
                    'unit': 'N/A',
                    'is_fasting_required': False,
                    'preparation_instructions': 'May require full bladder for pelvic scans',
                    'estimated_cost': test_data['b2b_price']
                }
            )
            if created:
                self.stdout.write(f'Created USG test: {test.name}')
            else:
                self.stdout.write(f'USG test already exists: {test.name}')
        
        # XRAY Tests
        xray_tests = [
            {'name': 'DISTAL LOOPOGRAM', 'code': 'XRAY-DISTAL-LOOP', 'lab_price': 1500, 'discount': 0.2, 'b2b_price': 1200},
            {'name': 'SCANOGRAM BILATERAL LOWER LIMB', 'code': 'XRAY-SCANOGRAM-BILAT-LL', 'lab_price': 2500, 'discount': 0.2, 'b2b_price': 2000},
            {'name': 'SCANOGRAM SINGLE LIMB', 'code': 'XRAY-SCANOGRAM-SINGLE', 'lab_price': 1500, 'discount': 0.2, 'b2b_price': 1200},
            {'name': 'SCANOGRAM WHOLE SPINE', 'code': 'XRAY-SCANOGRAM-SPINE', 'lab_price': 1500, 'discount': 0.2, 'b2b_price': 1200},
            {'name': 'XRAY IVP', 'code': 'XRAY-IVP', 'lab_price': 3000, 'discount': 0.2, 'b2b_price': 2400},
            {'name': 'XRAY ABDOMEN ERRECT', 'code': 'XRAY-ABD-ERRECT', 'lab_price': 250, 'discount': 0.2, 'b2b_price': 200},
            {'name': 'XRAY ANKLE AP & LAT', 'code': 'XRAY-ANKLE-AP-LAT', 'lab_price': 400, 'discount': 0.2, 'b2b_price': 320},
            {'name': 'XRAY ANKLE AP OR LAT', 'code': 'XRAY-ANKLE-AP-OR-LAT', 'lab_price': 250, 'discount': 0.2, 'b2b_price': 200},
            {'name': 'XRAY ANKLE JOINT AP & LAT', 'code': 'XRAY-ANKLE-JOINT-AP-LAT', 'lab_price': 400, 'discount': 0.2, 'b2b_price': 320},
            {'name': 'XRAY ANKLE JOINT AP OR LAT', 'code': 'XRAY-ANKLE-JOINT-AP-OR-LAT', 'lab_price': 250, 'discount': 0.2, 'b2b_price': 200},
            {'name': 'XRAY BARIUM ENEMA', 'code': 'XRAY-BARIUM-ENEMA', 'lab_price': 1200, 'discount': 0.2, 'b2b_price': 960},
            {'name': 'XRAY BARIUM MEAL FOLLOW THROUGH', 'code': 'XRAY-BARIUM-MEAL-FT', 'lab_price': 2000, 'discount': 0.2, 'b2b_price': 1600},
            {'name': 'XRAY BARIUM MEAL STUDY OF STOMACH & DUODENUM', 'code': 'XRAY-BARIUM-MEAL-STOMACH', 'lab_price': 2000, 'discount': 0.2, 'b2b_price': 1600},
            {'name': 'XRAY BARIUM SWALLOW STUDY OF OESOPHAGUS', 'code': 'XRAY-BARIUM-SWALLOW', 'lab_price': 1000, 'discount': 0.2, 'b2b_price': 800},
            {'name': 'XRAY BOTH KNEE AP & LAT', 'code': 'XRAY-BOTH-KNEE-AP-LAT', 'lab_price': 600, 'discount': 0.2, 'b2b_price': 480},
            {'name': 'XRAY BOTH KNEE STANDING OR SITING POSITION', 'code': 'XRAY-BOTH-KNEE-STANDING', 'lab_price': 300, 'discount': 0.2, 'b2b_price': 240},
            {'name': 'XRAY C. SPINE AP & LAT', 'code': 'XRAY-CSPINE-AP-LAT', 'lab_price': 400, 'discount': 0.2, 'b2b_price': 320},
            {'name': 'XRAY C. SPINE AP OR LAT', 'code': 'XRAY-CSPINE-AP-OR-LAT', 'lab_price': 250, 'discount': 0.2, 'b2b_price': 200},
            {'name': 'XRAY CHEST AP& LAT VIEW', 'code': 'XRAY-CHEST-AP-LAT', 'lab_price': 400, 'discount': 0.2, 'b2b_price': 320},
            {'name': 'XRAY CHEST PA / AP VIEW', 'code': 'XRAY-CHEST-PA-AP', 'lab_price': 250, 'discount': 0.2, 'b2b_price': 200},
            {'name': 'XRAY CHEST PA AP VIEW', 'code': 'XRAY-CHEST-PA-AP-VIEW', 'lab_price': 250, 'discount': 0.2, 'b2b_price': 200},
            {'name': 'XRAY DL SPINE AP & LAT', 'code': 'XRAY-DLSPINE-AP-LAT', 'lab_price': 400, 'discount': 0.2, 'b2b_price': 320},
            {'name': 'XRAY DL SPINE AP OR LAT', 'code': 'XRAY-DLSPINE-AP-OR-LAT', 'lab_price': 250, 'discount': 0.2, 'b2b_price': 200},
            {'name': 'XRAY ELBOW AP & LAT', 'code': 'XRAY-ELBOW-AP-LAT', 'lab_price': 400, 'discount': 0.2, 'b2b_price': 320},
            {'name': 'XRAY ELBOW AP OR LAT', 'code': 'XRAY-ELBOW-AP-OR-LAT', 'lab_price': 250, 'discount': 0.2, 'b2b_price': 200},
            {'name': 'XRAY FISTULOGRAM', 'code': 'XRAY-FISTULOGRAM', 'lab_price': 1200, 'discount': 0.2, 'b2b_price': 960},
            {'name': 'XRAY FLEXION VIEW', 'code': 'XRAY-FLEXION-VIEW', 'lab_price': 250, 'discount': 0.2, 'b2b_price': 200},
            {'name': 'XRAY FOOT AP & LAT', 'code': 'XRAY-FOOT-AP-LAT', 'lab_price': 400, 'discount': 0.2, 'b2b_price': 320},
            {'name': 'XRAY HAND AP & LAT', 'code': 'XRAY-HAND-AP-LAT', 'lab_price': 400, 'discount': 0.2, 'b2b_price': 320},
            {'name': 'XRAY HAND AP/LAT', 'code': 'XRAY-HAND-AP-LAT-ALT', 'lab_price': 300, 'discount': 0.2, 'b2b_price': 240},
            {'name': 'XRAY HIP JOINT', 'code': 'XRAY-HIP-JOINT', 'lab_price': 300, 'discount': 0.2, 'b2b_price': 240},
            {'name': 'XRAY HSG', 'code': 'XRAY-HSG', 'lab_price': 3000, 'discount': 0.2, 'b2b_price': 2400},
            {'name': 'XRAY KNEE AP & LAT', 'code': 'XRAY-KNEE-AP-LAT', 'lab_price': 400, 'discount': 0.2, 'b2b_price': 320},
            {'name': 'XRAY KNEE AP OR LAT', 'code': 'XRAY-KNEE-AP-OR-LAT', 'lab_price': 250, 'discount': 0.2, 'b2b_price': 200},
            {'name': 'XRAY KUB', 'code': 'XRAY-KUB', 'lab_price': 250, 'discount': 0.2, 'b2b_price': 200},
            {'name': 'XRAY LEG AP & LAT', 'code': 'XRAY-LEG-AP-LAT', 'lab_price': 500, 'discount': 0.2, 'b2b_price': 400},
            {'name': 'XRAY LS SPINE AP & LAT', 'code': 'XRAY-LSSPINE-AP-LAT', 'lab_price': 400, 'discount': 0.2, 'b2b_price': 320},
            {'name': 'XRAY LS SPINE AP OR LAT', 'code': 'XRAY-LSSPINE-AP-OR-LAT', 'lab_price': 250, 'discount': 0.2, 'b2b_price': 200},
            {'name': 'XRAY LS SPINE EXTENSION VIEW', 'code': 'XRAY-LSSPINE-EXTENSION', 'lab_price': 250, 'discount': 0.2, 'b2b_price': 200},
            {'name': 'XRAY MANDIBLE / JAW AP/LAT.', 'code': 'XRAY-MANDIBLE-JAW', 'lab_price': 400, 'discount': 0.2, 'b2b_price': 320},
            {'name': 'XRAY MASTOID', 'code': 'XRAY-MASTOID', 'lab_price': 300, 'discount': 0.2, 'b2b_price': 240},
            {'name': 'XRAY MCU', 'code': 'XRAY-MCU', 'lab_price': 1800, 'discount': 0.2, 'b2b_price': 1440},
            {'name': 'XRAY NASAL BONE (AP/LAT)', 'code': 'XRAY-NASAL-BONE', 'lab_price': 400, 'discount': 0.2, 'b2b_price': 320},
            {'name': 'XRAY NASOPHARYNX (AP/LAT)', 'code': 'XRAY-NASOPHARYNX', 'lab_price': 400, 'discount': 0.2, 'b2b_price': 320},
            {'name': 'XRAY NECK AP AND LAT', 'code': 'XRAY-NECK-AP-LAT', 'lab_price': 400, 'discount': 0.2, 'b2b_price': 320},
            {'name': 'XRAY NECK AP OR LAT', 'code': 'XRAY-NECK-AP-OR-LAT', 'lab_price': 250, 'discount': 0.2, 'b2b_price': 200},
            {'name': 'XRAY ORBIT (PA & OPTIC)', 'code': 'XRAY-ORBIT-PA-OPTIC', 'lab_price': 400, 'discount': 0.2, 'b2b_price': 320},
            {'name': 'XRAY PELVIS WITH BOTH HIPS', 'code': 'XRAY-PELVIS-BOTH-HIPS', 'lab_price': 300, 'discount': 0.2, 'b2b_price': 240},
            {'name': 'XRAY PNS', 'code': 'XRAY-PNS', 'lab_price': 250, 'discount': 0.2, 'b2b_price': 200},
            {'name': 'XRAY RGU', 'code': 'XRAY-RGU', 'lab_price': 1000, 'discount': 0.2, 'b2b_price': 800},
            {'name': 'XRAY SHOULDER AP & LAT', 'code': 'XRAY-SHOULDER-AP-LAT', 'lab_price': 450, 'discount': 0.2, 'b2b_price': 360},
            {'name': 'XRAY SI JOINT', 'code': 'XRAY-SI-JOINT', 'lab_price': 300, 'discount': 0.2, 'b2b_price': 240},
            {'name': 'XRAY SINOGRAM', 'code': 'XRAY-SINOGRAM', 'lab_price': 1200, 'discount': 0.2, 'b2b_price': 960},
            {'name': 'XRAY SKULL AP OR LAT', 'code': 'XRAY-SKULL-AP-OR-LAT', 'lab_price': 250, 'discount': 0.2, 'b2b_price': 200},
            {'name': 'XRAY SKULL AP& LAT', 'code': 'XRAY-SKULL-AP-LAT', 'lab_price': 500, 'discount': 0.2, 'b2b_price': 400},
            {'name': 'XRAY SPINE AP / LAT / OBLIQUE VIEW', 'code': 'XRAY-SPINE-AP-LAT-OBLIQUE', 'lab_price': 250, 'discount': 0.2, 'b2b_price': 200},
            {'name': 'XRAY T TUBE CHOLONGIOGRAM', 'code': 'XRAY-TTUBE-CHOLANGIO', 'lab_price': 1000, 'discount': 0.2, 'b2b_price': 800},
            {'name': 'XRAY THIGH', 'code': 'XRAY-THIGH', 'lab_price': 300, 'discount': 0.2, 'b2b_price': 240},
            {'name': 'XRAY TOES', 'code': 'XRAY-TOES', 'lab_price': 300, 'discount': 0.2, 'b2b_price': 240},
            {'name': 'XRAY WRIST JOINT AP & LAT', 'code': 'XRAY-WRIST-AP-LAT', 'lab_price': 400, 'discount': 0.2, 'b2b_price': 320},
            {'name': 'XRAY1 PLATE', 'code': 'XRAY-1PLATE', 'lab_price': 300, 'discount': 0.2, 'b2b_price': 240},
            {'name': 'XRAY2 PLATE', 'code': 'XRAY-2PLATE', 'lab_price': 400, 'discount': 0.2, 'b2b_price': 320},
        ]
        
        for test_data in xray_tests:
            test, created = InvestigationTest.objects.get_or_create(
                name=test_data['name'],
                category=xray_category,
                defaults={
                    'code': test_data['code'],
                    'description': f"X-ray: {test_data['name']}",
                    'normal_range': 'Normal findings',
                    'unit': 'N/A',
                    'is_fasting_required': False,
                    'preparation_instructions': 'Remove metal objects, may require contrast',
                    'estimated_cost': test_data['b2b_price']
                }
            )
            if created:
                self.stdout.write(f'Created XRAY test: {test.name}')
            else:
                self.stdout.write(f'XRAY test already exists: {test.name}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully populated all USG and XRAY tests!')
        )
        
        self.stdout.write('All investigation tests from the pricelist have been added to the database.')
