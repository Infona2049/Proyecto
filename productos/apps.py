from django.apps import AppConfig


class ProductosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'productos'
    def ready(self):
        # Import signals to register handlers
        try:
            import productos.signals  # noqa: F401
        except Exception:
            pass
