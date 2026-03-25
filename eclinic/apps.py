from django.apps import AppConfig


class EclinicConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'eclinic'
    
    def ready(self):
        """Import signals when the app is ready"""
        import eclinic.signals
