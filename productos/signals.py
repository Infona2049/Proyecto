from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from .models import Producto, HistorialInventario
import json
from decimal import Decimal, InvalidOperation

# Caché temporal para almacenar el estado previo al guardado
_PRE_SAVE_CACHE = {}


@receiver(pre_save, sender=Producto)
def producto_pre_save(sender, instance, **kwargs):
    """
    Antes de guardar, almacenamos el estado previo (si existe) para comparar
    y detectar qué campos cambiaron.
    """
    if instance.pk:
        try:
            prev = Producto.objects.get(pk=instance.pk)
            # Guardar una representación simple de los campos que nos interesan
            _PRE_SAVE_CACHE[instance.pk] = {
                'nombre_producto': prev.nombre_producto,
                'categoria_producto': prev.categoria_producto,
                'modelo_producto': prev.modelo_producto,
                'color_producto': prev.color_producto,
                'capacidad_producto': prev.capacidad_producto,
                'descripcion_producto': prev.descripcion_producto,
                'precio_producto': str(prev.precio_producto) if prev.precio_producto is not None else None,
                'codigo_barras_producto': prev.codigo_barras_producto,
            }
        except Producto.DoesNotExist:
            pass


@receiver(post_save, sender=Producto)
def producto_saved(sender, instance, created, **kwargs):
    """
    Crear un registro en `HistorialInventario`.
    Si es una edición, intentar incluir en `detalles` un JSON con los campos
    que cambiaron: {campo: [antes, despues], ...}
    """
    try:
        if created:
            HistorialInventario.objects.create(
                producto_id=instance.pk,
                nombre_producto=instance.nombre_producto or '',
                accion='added',
            )
            return

        # Edición: comparar con valores previos si existen
        modificaciones = {}
        prev = _PRE_SAVE_CACHE.pop(instance.pk, None)
        # Si el guardado fue marcado para suprimir historial desde la vista,
        # limpiamos la caché previa y no creamos el registro aquí.
        if getattr(instance, '_suppress_historial', False):
            # prev ya está consumido por el pop; nada más que hacer
            return

        if prev:
            # Campos a comprobar - mantener en sincronía con lo almacenado en pre_save
            campos = ['nombre_producto', 'categoria_producto', 'modelo_producto', 'color_producto',
                      'capacidad_producto', 'descripcion_producto', 'precio_producto', 'codigo_barras_producto']
            for campo in campos:
                antes = prev.get(campo)
                despues = getattr(instance, campo)

                # Ambos nulos → sin cambio
                if antes is None and despues is None:
                    continue

                # Comparación especializada para precio usando Decimal
                if campo == 'precio_producto':
                    try:
                        antes_dec = Decimal(str(antes)) if antes is not None else None
                    except (InvalidOperation, TypeError):
                        antes_dec = None
                    try:
                        despues_dec = Decimal(str(despues)) if despues is not None else None
                    except (InvalidOperation, TypeError):
                        despues_dec = None

                    if antes_dec != despues_dec:
                        # Guardar representación con dos decimales cuando sea posible
                        antes_s = format(antes_dec, 'f') if antes_dec is not None else None
                        despues_s = format(despues_dec, 'f') if despues_dec is not None else None
                        modificaciones[campo] = [antes_s, despues_s]
                    continue

                # Para otros campos comparar stringificados (None manejado arriba)
                antes_s = str(antes) if antes is not None else None
                despues_s = str(despues) if despues is not None else None

                if antes_s != despues_s:
                    modificaciones[campo] = [antes_s, despues_s]

        # Solo crear registro 'edited' si hubo modificaciones reales
        if modificaciones:
            HistorialInventario.objects.create(
                producto_id=instance.pk,
                nombre_producto=instance.nombre_producto or '',
                accion='edited',
                detalles=json.dumps(modificaciones, ensure_ascii=False),
            )
    except Exception:
        # Evitar que errores en señales rompan la operación principal
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
