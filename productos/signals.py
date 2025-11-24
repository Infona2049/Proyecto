from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Producto, HistorialInventario

@receiver(post_save, sender=Producto)
def producto_saved(sender, instance, created, **kwargs):
    try:
        accion = 'added' if created else 'edited'
        HistorialInventario.objects.create(
            producto_id=instance.pk,
            nombre_producto=instance.nombre_producto or '',
            accion=accion,
        )
    except Exception:
        # Avoid crashing on signal errors
        pass

@receiver(post_delete, sender=Producto)
def producto_deleted(sender, instance, **kwargs):
    try:
        HistorialInventario.objects.create(
            producto_id=instance.pk,
            nombre_producto=instance.nombre_producto or '',
            accion='deleted',
        )
    except Exception:
        pass
