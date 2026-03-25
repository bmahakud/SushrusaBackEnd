from django.core.management.base import BaseCommand
from django.conf import settings
import boto3
import os
from botocore.exceptions import ClientError, NoCredentialsError

class Command(BaseCommand):
    help = 'Set up and test DigitalOcean Spaces configuration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test-connection',
            action='store_true',
            help='Test the connection to DigitalOcean Spaces',
        )
        parser.add_argument(
            '--create-bucket',
            action='store_true',
            help='Create the bucket if it does not exist',
        )
        parser.add_argument(
            '--list-buckets',
            action='store_true',
            help='List all available buckets',
        )

    def handle(self, *args, **options):
        if not getattr(settings, 'USE_DIGITALOCEAN_SPACES', False):
            self.stdout.write(
                self.style.ERROR('DigitalOcean Spaces is not enabled. Set USE_DIGITALOCEAN_SPACES=True')
            )
            return

        # Get credentials
        access_key = getattr(settings, 'AWS_ACCESS_KEY_ID', '')
        secret_key = getattr(settings, 'AWS_SECRET_ACCESS_KEY', '')
        bucket_name = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', '')
        endpoint_url = getattr(settings, 'AWS_S3_ENDPOINT_URL', '')

        if not all([access_key, secret_key, bucket_name, endpoint_url]):
            self.stdout.write(
                self.style.ERROR('Missing DigitalOcean Spaces credentials. Please set:')
            )
            self.stdout.write('DO_SPACES_KEY=your_access_key')
            self.stdout.write('DO_SPACES_SECRET=your_secret_key')
            self.stdout.write('DO_SPACES_BUCKET=your_bucket_name')
            self.stdout.write('DO_SPACES_ENDPOINT=https://nyc3.digitaloceanspaces.com')
            return

        # Create S3 client
        try:
            session = boto3.session.Session()
            client = session.client(
                's3',
                region_name='nyc3',  # DigitalOcean Spaces region
                endpoint_url=endpoint_url,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to create S3 client: {e}')
            )
            return

        # List buckets
        if options['list_buckets']:
            try:
                response = client.list_buckets()
                self.stdout.write(self.style.SUCCESS('Available buckets:'))
                for bucket in response['Buckets']:
                    self.stdout.write(f'  - {bucket["Name"]}')
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to list buckets: {e}')
                )

        # Test connection
        if options['test_connection']:
            try:
                # Try to list objects in the bucket
                response = client.list_objects_v2(Bucket=bucket_name, MaxKeys=1)
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully connected to bucket: {bucket_name}')
                )
                self.stdout.write(f'Endpoint: {endpoint_url}')
                self.stdout.write(f'Objects in bucket: {response.get("KeyCount", 0)}')
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == 'NoSuchBucket':
                    self.stdout.write(
                        self.style.WARNING(f'Bucket {bucket_name} does not exist')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f'Failed to access bucket: {e}')
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Connection test failed: {e}')
                )

        # Create bucket
        if options['create_bucket']:
            try:
                client.create_bucket(Bucket=bucket_name)
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created bucket: {bucket_name}')
                )
                
                # Set bucket to public read
                bucket_policy = {
                    'Version': '2012-10-17',
                    'Statement': [
                        {
                            'Sid': 'PublicReadGetObject',
                            'Effect': 'Allow',
                            'Principal': '*',
                            'Action': 's3:GetObject',
                            'Resource': f'arn:aws:s3:::{bucket_name}/*'
                        }
                    ]
                }
                
                client.put_bucket_policy(
                    Bucket=bucket_name,
                    Policy=str(bucket_policy).replace("'", '"')
                )
                self.stdout.write(
                    self.style.SUCCESS('Set bucket to public read access')
                )
                
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == 'BucketAlreadyExists':
                    self.stdout.write(
                        self.style.WARNING(f'Bucket {bucket_name} already exists')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f'Failed to create bucket: {e}')
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to create bucket: {e}')
                )

        if not any([options['test_connection'], options['create_bucket'], options['list_buckets']]):
            self.stdout.write(self.style.SUCCESS('DigitalOcean Spaces configuration:'))
            self.stdout.write(f'  Endpoint: {endpoint_url}')
            self.stdout.write(f'  Bucket: {bucket_name}')
            self.stdout.write(f'  Access Key: {access_key[:10]}...')
            self.stdout.write('')
            self.stdout.write('Available commands:')
            self.stdout.write('  python manage.py setup_digitalocean_spaces --test-connection')
            self.stdout.write('  python manage.py setup_digitalocean_spaces --create-bucket')
            self.stdout.write('  python manage.py setup_digitalocean_spaces --list-buckets') 