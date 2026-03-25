from django.core.management.base import BaseCommand
from django.conf import settings
import os
import re


class Command(BaseCommand):
    help = 'Toggle OTP test mode on/off for development testing'

    def add_arguments(self, parser):
        parser.add_argument('--on', action='store_true', help='Enable OTP test mode')
        parser.add_argument('--off', action='store_true', help='Disable OTP test mode')
        parser.add_argument('--status', action='store_true', help='Check current OTP test mode status')
        parser.add_argument('--test-code', type=str, default='999999', help='Set custom test OTP code (default: 999999)')

    def handle(self, *args, **options):
        settings_file = 'myproject/settings.py'
        
        if not os.path.exists(settings_file):
            self.stdout.write(
                self.style.ERROR(f'Settings file not found: {settings_file}')
            )
            return

        # Read current settings
        with open(settings_file, 'r') as f:
            content = f.read()

        # Check current status
        current_test_mode = 'OTP_TEST_MODE = True' in content
        current_test_code = '999999'  # default
        
        # Extract current test code if it exists
        test_code_match = re.search(r'OTP_TEST_CODE\s*=\s*[\'"]([^\'"]+)[\'"]', content)
        if test_code_match:
            current_test_code = test_code_match.group(1)

        if options['status']:
            self.stdout.write(
                self.style.SUCCESS(f'Current OTP Test Mode: {"ENABLED" if current_test_mode else "DISABLED"}')
            )
            self.stdout.write(f'Current Test OTP Code: {current_test_code}')
            return

        # Determine action
        if options['on']:
            action = 'enable'
        elif options['off']:
            action = 'disable'
        else:
            # Default: toggle current state
            action = 'disable' if current_test_mode else 'enable'

        test_code = options['test_code']

        if action == 'enable':
            # Add or update OTP_TEST_MODE = True
            if 'OTP_TEST_MODE = True' in content:
                self.stdout.write(
                    self.style.WARNING('OTP test mode is already enabled')
                )
            else:
                # Remove existing OTP_TEST_MODE = False if it exists
                content = re.sub(r'OTP_TEST_MODE\s*=\s*False', '', content)
                
                # Add OTP_TEST_MODE = True and OTP_TEST_CODE
                # Find a good place to add it (after other settings)
                if '# OTP Configuration' in content:
                    # Replace existing OTP section
                    content = re.sub(
                        r'# OTP Configuration.*?OTP_TEST_CODE.*?\n',
                        f'# OTP Configuration\nOTP_TEST_MODE = True\nOTP_TEST_CODE = \'{test_code}\'\n',
                        content,
                        flags=re.DOTALL
                    )
                else:
                    # Add new OTP section before the last line
                    lines = content.split('\n')
                    insert_index = len(lines) - 1
                    for i, line in enumerate(lines):
                        if line.strip() == '' and i > len(lines) - 10:  # Near the end
                            insert_index = i
                            break
                    
                    lines.insert(insert_index, '')
                    lines.insert(insert_index, f"OTP_TEST_CODE = '{test_code}'")
                    lines.insert(insert_index, 'OTP_TEST_MODE = True')
                    lines.insert(insert_index, '# OTP Configuration')
                    content = '\n'.join(lines)

                self.stdout.write(
                    self.style.SUCCESS(f'OTP test mode ENABLED with test code: {test_code}')
                )

        else:  # disable
            # Remove OTP_TEST_MODE and OTP_TEST_CODE
            content = re.sub(r'OTP_TEST_MODE\s*=\s*True', '', content)
            content = re.sub(r'OTP_TEST_CODE\s*=\s*[\'"][^\'"]+[\'"]', '', content)
            content = re.sub(r'# OTP Configuration\n', '', content)
            
            # Clean up extra empty lines
            content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
            
            self.stdout.write(
                self.style.SUCCESS('OTP test mode DISABLED - using production SMS')
            )

        # Write back to settings file
        with open(settings_file, 'w') as f:
            f.write(content)

        # Show usage instructions
        if action == 'enable':
            self.stdout.write('\n' + '='*50)
            self.stdout.write(self.style.SUCCESS('OTP TEST MODE ENABLED'))
            self.stdout.write('='*50)
            self.stdout.write(f'Test OTP Code: {test_code}')
            self.stdout.write('')
            self.stdout.write('Usage:')
            self.stdout.write('1. Send OTP: POST /api/auth/send-otp/')
            self.stdout.write('2. Verify OTP: POST /api/auth/verify-otp/ with OTP: ' + test_code)
            self.stdout.write('')
            self.stdout.write('To disable test mode: python manage.py toggle_otp_test_mode --off')
            self.stdout.write('='*50)
        else:
            self.stdout.write('\n' + '='*50)
            self.stdout.write(self.style.SUCCESS('OTP TEST MODE DISABLED'))
            self.stdout.write('='*50)
            self.stdout.write('Now using production SMS for OTP delivery')
            self.stdout.write('')
            self.stdout.write('To enable test mode: python manage.py toggle_otp_test_mode --on')
            self.stdout.write('='*50) 