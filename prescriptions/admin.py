from django.contrib import admin
from .models import Prescription, PrescriptionMedication, PrescriptionVitalSigns, PrescriptionPDF, InvestigationCategory, InvestigationTest, PrescriptionInvestigation, PrescriptionImage


class PrescriptionMedicationInline(admin.TabularInline):
    model = PrescriptionMedication
    extra = 1
    fields = [
        'medicine_name', 'composition', 'dosage_form',
        'morning_dose', 'afternoon_dose', 'evening_dose',
        'frequency', 'timing', 'duration_days', 'special_instructions'
    ]


class PrescriptionVitalSignsInline(admin.StackedInline):
    model = PrescriptionVitalSigns
    extra = 0


class PrescriptionPDFInline(admin.TabularInline):
    model = PrescriptionPDF
    extra = 0
    readonly_fields = ['version_number', 'generated_at', 'file_size', 'checksum']
    fields = ['version_number', 'is_current', 'pdf_file', 'generated_by', 'generated_at', 'file_size']


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'patient', 'doctor', 'issued_date', 'primary_diagnosis', 
        'is_draft', 'is_finalized', 'created_at'
    ]
    list_filter = [
        'is_draft', 'is_finalized', 'issued_date', 'created_at',
        'doctor__role'
    ]
    search_fields = [
        'patient__name', 'patient__phone', 'doctor__name', 
        'primary_diagnosis', 'patient_previous_history'
    ]
    readonly_fields = ['issued_date', 'issued_time', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                ('consultation', 'doctor', 'patient'),
                ('issued_date', 'issued_time'),
                ('is_draft', 'is_finalized')
            )
        }),
        ('Vital Signs', {
            'fields': (
                ('pulse', 'temperature'),
                ('blood_pressure_systolic', 'blood_pressure_diastolic'),
                ('weight', 'height')
            ),
            'classes': ('collapse',)
        }),
        ('Diagnosis', {
            'fields': (
                'primary_diagnosis',
                'patient_previous_history',
                'clinical_classification'
            )
        }),
        ('Instructions', {
            'fields': (
                'general_instructions',
                'fluid_intake',
                'diet_instructions',
                'lifestyle_advice'
            ),
            'classes': ('collapse',)
        }),
        ('Follow-up', {
            'fields': (
                'next_visit',
                'follow_up_notes'
            ),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        })
    )
    
    inlines = [PrescriptionMedicationInline, PrescriptionVitalSignsInline, PrescriptionPDFInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'doctor', 'patient', 'consultation'
        ).prefetch_related('medications', 'vital_signs', 'pdf_versions')


@admin.register(PrescriptionPDF)
class PrescriptionPDFAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'prescription', 'version_number', 'is_current', 
        'generated_by', 'generated_at', 'file_size'
    ]
    list_filter = [
        'is_current', 'generated_at', 'generated_by__role'
    ]
    search_fields = [
        'prescription__patient__name', 'prescription__doctor__name',
        'generated_by__name'
    ]
    readonly_fields = [
        'version_number', 'generated_at', 'file_size', 'checksum'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'prescription',
                ('version_number', 'is_current'),
                'generated_by',
                'generated_at'
            )
        }),
        ('PDF File', {
            'fields': (
                'pdf_file',
                ('file_size', 'checksum')
            )
        }),
        ('Template Images', {
            'fields': (
                'header_image',
                'footer_image'
            ),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'prescription', 'generated_by', 'prescription__patient', 'prescription__doctor'
        )


@admin.register(PrescriptionMedication)
class PrescriptionMedicationAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'prescription', 'medicine_name', 'frequency', 
        'duration_days', 'order'
    ]
    list_filter = ['frequency', 'timing', 'is_continuous']
    search_fields = ['medicine_name', 'composition', 'prescription__patient__name']
    ordering = ['prescription', 'order']


@admin.register(PrescriptionVitalSigns)
class PrescriptionVitalSignsAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'prescription', 'pulse', 'blood_pressure_display',
        'temperature', 'weight'
    ]
    search_fields = ['prescription__patient__name', 'prescription__doctor__name']
    
    def blood_pressure_display(self, obj):
        if obj.blood_pressure_systolic and obj.blood_pressure_diastolic:
            return f"{obj.blood_pressure_systolic}/{obj.blood_pressure_diastolic}"
        return "-"
    blood_pressure_display.short_description = "Blood Pressure"


@admin.register(InvestigationCategory)
class InvestigationCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'is_active', 'order', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['order', 'name']
    list_editable = ['is_active', 'order']


@admin.register(InvestigationTest)
class InvestigationTestAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'code', 'is_fasting_required', 'estimated_cost', 'is_active', 'order']
    list_filter = ['category', 'is_fasting_required', 'is_active', 'created_at']
    search_fields = ['name', 'code', 'description']
    ordering = ['category__order', 'order', 'name']
    list_editable = ['is_active', 'order', 'is_fasting_required']
    autocomplete_fields = ['category']


@admin.register(PrescriptionInvestigation)
class PrescriptionInvestigationAdmin(admin.ModelAdmin):
    list_display = ['prescription', 'test', 'priority', 'order', 'created_at']
    list_filter = ['priority', 'created_at']
    search_fields = ['prescription__id', 'test__name']
    ordering = ['prescription', 'order']
    autocomplete_fields = ['prescription', 'test']


@admin.register(PrescriptionImage)
class PrescriptionImageAdmin(admin.ModelAdmin):
    list_display = ['prescription', 'uploaded_by', 'uploaded_at', 'is_mobile_upload']
    list_filter = ['is_mobile_upload', 'uploaded_at']
    search_fields = ['prescription__id', 'uploaded_by__username']
    ordering = ['-uploaded_at']
    readonly_fields = ['uploaded_at']
    autocomplete_fields = ['prescription', 'uploaded_by']
