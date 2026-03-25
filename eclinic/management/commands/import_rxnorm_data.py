import csv
import zipfile
import os
import requests
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from eclinic.models import GlobalMedication
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Import medications from RxNorm database'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help='Path to RxNorm data file (zip or csv)'
        )
        parser.add_argument(
            '--download',
            action='store_true',
            help='Download latest RxNorm data automatically'
        )
        parser.add_argument(
            '--update-existing',
            action='store_true',
            help='Update existing medications instead of skipping'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=1000,
            help='Limit number of medications to import (default: 1000)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be imported without actually importing'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting RxNorm medication import...')
        )
        
        # Download data if requested
        if options['download']:
            file_path = self.download_rxnorm_data()
        else:
            file_path = options['file']
        
        if not file_path or not os.path.exists(file_path):
            raise CommandError('RxNorm data file not found. Use --download or provide --file path.')
        
        # Process the data
        self.process_rxnorm_data(
            file_path,
            update_existing=options['update_existing'],
            limit=options['limit'],
            dry_run=options['dry_run']
        )
    
    def download_rxnorm_data(self):
        """Download latest RxNorm data"""
        self.stdout.write('Downloading latest RxNorm data...')
        
        # Get current date for filename
        current_date = datetime.now().strftime('%Y%m')
        url = f'https://download.nlm.nih.gov/umls/kss/rxnorm/RxNorm_full_{current_date}.zip'
        
        # Create downloads directory
        downloads_dir = 'downloads'
        os.makedirs(downloads_dir, exist_ok=True)
        
        file_path = os.path.join(downloads_dir, f'RxNorm_full_{current_date}.zip')
        
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            self.stdout.write(
                self.style.SUCCESS(f'Downloaded RxNorm data to {file_path}')
            )
            return file_path
            
        except requests.RequestException as e:
            self.stdout.write(
                self.style.WARNING(f'Failed to download from {url}: {e}')
            )
            # Try previous month
            prev_date = (datetime.now().replace(day=1) - timedelta(days=1)).strftime('%Y%m')
            url = f'https://download.nlm.nih.gov/umls/kss/rxnorm/RxNorm_full_{prev_date}.zip'
            
            self.stdout.write(f'Trying previous month: {url}')
            try:
                response = requests.get(url, stream=True)
                response.raise_for_status()
                
                file_path = os.path.join(downloads_dir, f'RxNorm_full_{prev_date}.zip')
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                self.stdout.write(
                    self.style.SUCCESS(f'Downloaded RxNorm data to {file_path}')
                )
                return file_path
                
            except requests.RequestException as e2:
                raise CommandError(f'Failed to download RxNorm data: {e2}')
    
    def process_rxnorm_data(self, file_path, update_existing=False, limit=1000, dry_run=False):
        """Process RxNorm data file"""
        self.stdout.write(f'Processing RxNorm data from {file_path}...')
        
        # Extract if it's a zip file
        if file_path.endswith('.zip'):
            extract_dir = file_path.replace('.zip', '_extracted')
            os.makedirs(extract_dir, exist_ok=True)
            
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            # Find the main RxNorm files
            rxnorm_files = []
            for root, dirs, files in os.walk(extract_dir):
                for file in files:
                    if file.startswith('RXNCONSO') or file.startswith('RXNST'):
                        rxnorm_files.append(os.path.join(root, file))
            
            if not rxnorm_files:
                raise CommandError('No RxNorm data files found in zip archive')
            
            # Use the first file found
            data_file = rxnorm_files[0]
        else:
            data_file = file_path
        
        # Process the data
        medications_processed = 0
        medications_created = 0
        medications_updated = 0
        errors = []
        
        try:
            with open(data_file, 'r', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile, delimiter='|')
                
                for row in reader:
                    if medications_processed >= limit:
                        break
                    
                    try:
                        medication_data = self.parse_rxnorm_row(row)
                        if medication_data:
                            if dry_run:
                                self.stdout.write(f'Would import: {medication_data["name"]}')
                                medications_created += 1
                            else:
                                result = self.import_medication(
                                    medication_data, 
                                    update_existing=update_existing
                                )
                                if result == 'created':
                                    medications_created += 1
                                elif result == 'updated':
                                    medications_updated += 1
                        
                        medications_processed += 1
                        
                        if medications_processed % 100 == 0:
                            self.stdout.write(
                                f'Processed {medications_processed} medications...'
                            )
                    
                    except Exception as e:
                        errors.append({
                            'row': row,
                            'error': str(e)
                        })
                        if len(errors) > 10:  # Limit error reporting
                            break
        
        except Exception as e:
            raise CommandError(f'Error processing RxNorm data: {e}')
        
        # Summary
        self.stdout.write(
            self.style.SUCCESS(
                f'\nImport Summary:\n'
                f'Total processed: {medications_processed}\n'
                f'Created: {medications_created}\n'
                f'Updated: {medications_updated}\n'
                f'Errors: {len(errors)}'
            )
        )
        
        if errors:
            self.stdout.write(
                self.style.WARNING(f'\nFirst few errors:\n')
            )
            for error in errors[:5]:
                self.stdout.write(f'Error: {error["error"]}')
    
    def parse_rxnorm_row(self, row):
        """Parse a row from RxNorm data file"""
        if len(row) < 16:
            return None
        
        # RxNorm CONSO.RRF format
        # Fields: RXCUI|LAT|TS|LUI|STT|SUI|ISPREF|RXAUI|SAUI|SCUI|SDUI|SAB|TTY|CODE|STR|SRL|SUPPRESS|CVF
        rxcui, lat, ts, lui, stt, sui, ispref, rxaui, saui, scui, sdui, sab, tty, code, str_name, srl, suppress, cvf = row[:17]
        
        # Only process English terms (LAT = ENG)
        if lat != 'ENG':
            return None
        
        # Only process preferred terms (ISPREF = Y)
        if ispref != 'Y':
            return None
        
        # Only process certain term types (TTY)
        # IN = Ingredient, PIN = Precise Ingredient, BN = Brand Name, SBD = Semantic Branded Drug, etc.
        valid_ttys = ['IN', 'PIN', 'BN', 'SBD', 'SCD', 'GPCK', 'BPCK']
        if tty not in valid_ttys:
            return None
        
        # Determine medication type
        if tty in ['IN', 'PIN']:
            medication_type = 'generic'
        elif tty in ['BN', 'SBD']:
            medication_type = 'branded'
        else:
            medication_type = 'combination'
        
        # Clean and standardize name
        name = str_name.strip()
        if not name or len(name) < 2:
            return None
        
        # Extract strength and form from name if possible
        strength = ''
        dosage_form = 'tablet'  # default
        
        # Common dosage forms
        forms = {
            'tablet': ['tablet', 'tab', 'tabs'],
            'capsule': ['capsule', 'cap', 'caps'],
            'syrup': ['syrup', 'suspension', 'liquid'],
            'injection': ['injection', 'injectable', 'vial'],
            'cream': ['cream', 'ointment', 'gel'],
            'drops': ['drops', 'eye drops', 'ear drops'],
            'inhaler': ['inhaler', 'inhalation'],
        }
        
        name_lower = name.lower()
        for form, keywords in forms.items():
            if any(keyword in name_lower for keyword in keywords):
                dosage_form = form
                break
        
        # Extract strength (common patterns: 500mg, 10mg/ml, etc.)
        import re
        strength_match = re.search(r'(\d+(?:\.\d+)?)\s*(mg|mcg|g|ml|mcg/ml|mg/ml|g/ml)', name, re.IGNORECASE)
        if strength_match:
            strength = f"{strength_match.group(1)}{strength_match.group(2)}"
        
        return {
            'name': name,
            'generic_name': name if medication_type == 'generic' else '',
            'brand_name': name if medication_type == 'branded' else '',
            'composition': '',
            'dosage_form': dosage_form,
            'strength': strength,
            'medication_type': medication_type,
            'therapeutic_class': '',
            'indication': '',
            'contraindications': '',
            'side_effects': '',
            'dosage_instructions': '',
            'frequency_options': ['once_daily', 'twice_daily', 'thrice_daily'],
            'timing_options': ['before_breakfast', 'after_breakfast', 'before_lunch', 'after_lunch', 'before_dinner', 'after_dinner', 'at_bedtime'],
            'manufacturer': '',
            'license_number': '',
            'is_prescription_required': True,
            'is_active': True,
            'is_verified': False,
            'rxcui': rxcui,
            'tty': tty,
            'sab': sab
        }
    
    @transaction.atomic
    def import_medication(self, medication_data, update_existing=False):
        """Import a single medication"""
        # Check if medication already exists
        existing = GlobalMedication.objects.filter(
            name__iexact=medication_data['name']
        ).first()
        
        if existing:
            if update_existing:
                # Update existing medication
                for field, value in medication_data.items():
                    if field not in ['rxcui', 'tty', 'sab']:  # Skip RxNorm-specific fields
                        setattr(existing, field, value)
                existing.updated_at = timezone.now()
                existing.save()
                return 'updated'
            else:
                return 'skipped'
        else:
            # Create new medication
            # Remove RxNorm-specific fields
            for field in ['rxcui', 'tty', 'sab']:
                medication_data.pop(field, None)
            
            GlobalMedication.objects.create(**medication_data)
            return 'created'
