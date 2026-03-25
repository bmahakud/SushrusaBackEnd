from django.apps import AppConfig


class PrescriptionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'prescriptions'
    
    def ready(self):
        """Import signals when the app is ready"""
        import prescriptions.signals
