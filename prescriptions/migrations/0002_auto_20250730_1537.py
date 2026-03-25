# Generated manually for prescription model enhancement

from django.db import migrations, models
import django.db.models.deletion
import django.core.validators
from django.utils import timezone

def set_default_issued_time(apps, schema_editor):
    """Set default issued_time for existing prescriptions"""
    Prescription = apps.get_model('prescriptions', 'Prescription')
    for prescription in Prescription.objects.all():
        prescription.issued_time = timezone.now().time()
        prescription.save()

class Migration(migrations.Migration):

    dependencies = [
        ('consultations', '0001_initial'),
        ('prescriptions', '0001_initial'),
    ]

    operations = [
        # Add consultation field
        migrations.AddField(
            model_name='prescription',
            name='consultation',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='prescriptions', to='consultations.consultation'),
        ),
        
        # Add issued_time field with default
        migrations.AddField(
            model_name='prescription',
            name='issued_time',
            field=models.TimeField(auto_now_add=True, default=timezone.now),
            preserve_default=False,
        ),
        
        # Add vital signs fields
        migrations.AddField(
            model_name='prescription',
            name='pulse',
            field=models.PositiveIntegerField(blank=True, help_text='Pulse rate in bpm', null=True),
        ),
        migrations.AddField(
            model_name='prescription',
            name='blood_pressure_systolic',
            field=models.PositiveIntegerField(blank=True, help_text='Systolic BP', null=True),
        ),
        migrations.AddField(
            model_name='prescription',
            name='blood_pressure_diastolic',
            field=models.PositiveIntegerField(blank=True, help_text='Diastolic BP', null=True),
        ),
        migrations.AddField(
            model_name='prescription',
            name='temperature',
            field=models.DecimalField(blank=True, decimal_places=1, help_text='Temperature in Celsius', max_digits=4, null=True),
        ),
        migrations.AddField(
            model_name='prescription',
            name='weight',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Weight in kg', max_digits=5, null=True),
        ),
        migrations.AddField(
            model_name='prescription',
            name='height',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Height in cm', max_digits=5, null=True),
        ),
        
        # Add diagnosis fields
        migrations.AddField(
            model_name='prescription',
            name='primary_diagnosis',
            field=models.TextField(blank=True, help_text='Primary diagnosis'),
        ),
        migrations.AddField(
            model_name='prescription',
            name='secondary_diagnosis',
            field=models.TextField(blank=True, help_text='Secondary diagnosis'),
        ),
        migrations.AddField(
            model_name='prescription',
            name='clinical_classification',
            field=models.TextField(blank=True, help_text='Clinical classification (e.g., NYHA Class)'),
        ),
        
        # Add instruction fields
        migrations.AddField(
            model_name='prescription',
            name='general_instructions',
            field=models.TextField(blank=True, help_text='General medication instructions'),
        ),
        migrations.AddField(
            model_name='prescription',
            name='fluid_intake',
            field=models.CharField(blank=True, help_text='Fluid intake instructions', max_length=100),
        ),
        migrations.AddField(
            model_name='prescription',
            name='diet_instructions',
            field=models.TextField(blank=True, help_text='Diet instructions'),
        ),
        migrations.AddField(
            model_name='prescription',
            name='lifestyle_advice',
            field=models.TextField(blank=True, help_text='Lifestyle advice'),
        ),
        
        # Add follow-up fields
        migrations.AddField(
            model_name='prescription',
            name='next_visit',
            field=models.CharField(blank=True, help_text='Next visit instructions', max_length=100),
        ),
        migrations.AddField(
            model_name='prescription',
            name='follow_up_notes',
            field=models.TextField(blank=True, help_text='Follow-up notes'),
        ),
        
        # Add status fields
        migrations.AddField(
            model_name='prescription',
            name='is_draft',
            field=models.BooleanField(default=True, help_text='Whether prescription is in draft mode'),
        ),
        migrations.AddField(
            model_name='prescription',
            name='is_finalized',
            field=models.BooleanField(default=False, help_text='Whether prescription is finalized'),
        ),
        
        # Add unique constraint
        migrations.AlterUniqueTogether(
            name='prescription',
            unique_together={('consultation', 'doctor', 'patient')},
        ),
        
        # Remove old fields
        migrations.RemoveField(
            model_name='prescription',
            name='header',
        ),
        migrations.RemoveField(
            model_name='prescription',
            name='footer',
        ),
        migrations.RemoveField(
            model_name='prescription',
            name='text',
        ),
        
        # Create PrescriptionMedication model
        migrations.CreateModel(
            name='PrescriptionMedication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('medicine_name', models.CharField(help_text='Name of the medicine', max_length=200)),
                ('composition', models.CharField(blank=True, help_text='Composition/ingredients', max_length=500)),
                ('dosage_form', models.CharField(blank=True, help_text='Tablet, Syrup, Injection, etc.', max_length=100)),
                ('morning_dose', models.PositiveIntegerField(default=0, help_text='Morning dose')),
                ('afternoon_dose', models.PositiveIntegerField(default=0, help_text='Afternoon dose')),
                ('evening_dose', models.PositiveIntegerField(default=0, help_text='Evening dose')),
                ('frequency', models.CharField(choices=[('once_daily', 'Once Daily'), ('twice_daily', 'Twice Daily'), ('thrice_daily', 'Thrice Daily'), ('four_times_daily', 'Four Times Daily'), ('sos', 'SOS (As Needed)'), ('custom', 'Custom')], default='once_daily', max_length=20)),
                ('timing', models.CharField(choices=[('before_breakfast', 'Before Breakfast'), ('after_breakfast', 'After Breakfast'), ('before_lunch', 'Before Lunch'), ('after_lunch', 'After Lunch'), ('before_dinner', 'Before Dinner'), ('after_dinner', 'After Dinner'), ('bedtime', 'Bedtime'), ('empty_stomach', 'Empty Stomach'), ('with_food', 'With Food'), ('custom', 'Custom')], default='after_breakfast', max_length=20)),
                ('custom_timing', models.CharField(blank=True, help_text='Custom timing instructions', max_length=200)),
                ('duration_days', models.PositiveIntegerField(blank=True, help_text='Duration in days', null=True)),
                ('duration_weeks', models.PositiveIntegerField(blank=True, help_text='Duration in weeks', null=True)),
                ('duration_months', models.PositiveIntegerField(blank=True, help_text='Duration in months', null=True)),
                ('is_continuous', models.BooleanField(default=False, help_text='Continue indefinitely')),
                ('special_instructions', models.TextField(blank=True, help_text='Special instructions for this medication')),
                ('notes', models.TextField(blank=True, help_text='Additional notes')),
                ('order', models.PositiveIntegerField(default=0, help_text='Order of medication in prescription')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('prescription', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='medications', to='prescriptions.prescription')),
            ],
            options={
                'verbose_name': 'Prescription Medication',
                'verbose_name_plural': 'Prescription Medications',
                'db_table': 'prescription_medications',
                'ordering': ['order', 'created_at'],
            },
        ),
        
        # Create PrescriptionVitalSigns model
        migrations.CreateModel(
            name='PrescriptionVitalSigns',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pulse', models.PositiveIntegerField(blank=True, help_text='Pulse rate in bpm', null=True)),
                ('blood_pressure_systolic', models.PositiveIntegerField(blank=True, help_text='Systolic BP', null=True)),
                ('blood_pressure_diastolic', models.PositiveIntegerField(blank=True, help_text='Diastolic BP', null=True)),
                ('temperature', models.DecimalField(blank=True, decimal_places=1, help_text='Temperature in Celsius', max_digits=4, null=True)),
                ('weight', models.DecimalField(blank=True, decimal_places=2, help_text='Weight in kg', max_digits=5, null=True)),
                ('height', models.DecimalField(blank=True, decimal_places=2, help_text='Height in cm', max_digits=5, null=True)),
                ('respiratory_rate', models.PositiveIntegerField(blank=True, help_text='Respiratory rate per minute', null=True)),
                ('oxygen_saturation', models.PositiveIntegerField(blank=True, help_text='Oxygen saturation percentage', null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('blood_sugar_fasting', models.DecimalField(blank=True, decimal_places=2, help_text='Fasting blood sugar', max_digits=5, null=True)),
                ('blood_sugar_postprandial', models.DecimalField(blank=True, decimal_places=2, help_text='Postprandial blood sugar', max_digits=5, null=True)),
                ('hba1c', models.DecimalField(blank=True, decimal_places=2, help_text='HbA1c percentage', max_digits=4, null=True)),
                ('notes', models.TextField(blank=True, help_text='Additional notes about vital signs')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('prescription', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='vital_signs', to='prescriptions.prescription')),
            ],
            options={
                'verbose_name': 'Prescription Vital Signs',
                'verbose_name_plural': 'Prescription Vital Signs',
                'db_table': 'prescription_vital_signs',
            },
        ),
    ]
