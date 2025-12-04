# ...existing code...
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.core.paginator import Paginator
from django.contrib import messages
from django.db import transaction
from django.db.models.deletion import ProtectedError
from django.utils import timezone
from datetime import datetime

# importar modelo DetalleFactura para borrado forzado de referencias
from facturas.models import DetalleFactura

# Importar modelos y formularios del mismo app
from .models import Inventario, Producto, HistorialInventario
from .forms import ProductoForm

# ---------------------------------------------------------------------
# Registro de productos
# ---------------------------------------------------------------------
def registro_producto_view(request):
    """
    Vista para registrar un nuevo Producto.
    - GET: muestra el formulario vacío.
    - POST: procesa el formulario, guarda Producto y crea un registro inicial en Inventario.
    - Al crear con éxito redirige a la misma vista con ?exito=1.
    """
    exito = request.GET.get('exito')
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save()
            # Obtener stock inicial (campo opcional del formulario)
            stock_actual = form.cleaned_data.get('stock_actual_inventario', 0) or 0
            Inventario.objects.create(
                producto=producto,
                stock_actual_inventario=stock_actual,
                stock_minimo_inventario=1,
                # usar nombre de campo del modelo Producto para código de barras
                codigo_barras_inventario=getattr(producto, 'codigo_barras_producto', getattr(producto, 'codigo_barras', ''))
            )
            return redirect(f"{reverse('registro_producto')}?exito=1")
    else:
        form = ProductoForm()

    return render(request, 'productos/registro_producto.html', {'form': form, 'exito': exito})

# ---------------------------------------------------------------------
# Listado / Inventario
# ---------------------------------------------------------------------
def inventario_view(request):
    """
    Muestra la lista paginada de Inventario.
    - Aplica filtros por categoria, color y capacidad si se pasan por GET.
    - Usa select_related para optimizar consultas hacia Producto relacionado.
    """
    inventarios = Inventario.objects.select_related('producto').order_by('fecha_actualizacion_inventario')

    # Filtros simples desde query params
    categoria = request.GET.get('categoria')
    color = request.GET.get('color')
    capacidad = request.GET.get('capacidad')

    if categoria:
        inventarios = inventarios.filter(producto__categoria_producto=categoria)
    if color:
        inventarios = inventarios.filter(producto__color_producto=color)
    if capacidad:
        inventarios = inventarios.filter(producto__capacidad_producto=capacidad)

    paginator = Paginator(inventarios, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'productos/inventario.html', {'inventarios': page_obj})

# ---------------------------------------------------------------------
# Edición de inventario / producto relacionado
# ---------------------------------------------------------------------
def editar_inventario_view(request, pk):
    """
    Actualiza los datos del Producto relacionado y del Inventario.
    - Se espera POST con los campos a actualizar.
    - Si no es POST, redirige a la vista de inventario (sin mostrar formulario aquí).
    """
    inventario = get_object_or_404(Inventario, pk=pk)

    if request.method != 'POST':
        return redirect('inventario')

    producto = inventario.producto

    # Guardar estado previo del producto para comparar y consolidar historial
    prev_product = {
        'nombre_producto': producto.nombre_producto,
        'categoria_producto': producto.categoria_producto,
        'modelo_producto': producto.modelo_producto,
        'color_producto': producto.color_producto,
        'capacidad_producto': producto.capacidad_producto,
        'descripcion_producto': producto.descripcion_producto,
        'precio_producto': str(producto.precio_producto) if producto.precio_producto is not None else None,
        'codigo_barras_producto': producto.codigo_barras_producto,
    }

    # Actualizar campos de producto si vienen en POST (mantener valores por defecto si faltan)
    producto.categoria_producto = request.POST.get('categoria_producto', producto.categoria_producto)
    producto.nombre_producto = request.POST.get('nombre_producto', producto.nombre_producto)
    producto.modelo_producto = request.POST.get('modelo_producto', producto.modelo_producto)
    producto.color_producto = request.POST.get('color_producto', producto.color_producto)
    producto.capacidad_producto = request.POST.get('capacidad_producto', producto.capacidad_producto)

    # Actualizar precio con conversión segura
    precio = request.POST.get('precio_producto')
    if precio is not None and precio != '':
        try:
            producto.precio_producto = float(precio)
        except (ValueError, TypeError):
            # Ignorar si la conversión falla
            pass

    # Marcar para suprimir la creación de historial desde la señal
    # porque nosotros vamos a crear un registro consolidado más abajo.
    try:
        setattr(producto, '_suppress_historial', True)
    except Exception:
        pass

    producto.save()

    # Procesar archivos enviados (imagen del producto / imagen del inventario)
    # Guardamos la imagen del producto si se ha enviado un archivo
    if 'imagen_producto' in request.FILES:
        try:
            producto.imagen_producto = request.FILES['imagen_producto']
            producto.save()
        except Exception:
            # No bloquear la edición por errores en la subida; podríamos loguear
            pass

    # Si se envía imagen específica para inventario, manejarla también
    if 'imagen_inventario' in request.FILES:
        try:
            inventario.imagen_inventario = request.FILES['imagen_inventario']
        except Exception:
            pass

    # Actualizar campos de inventario (intentar convertir a int si procede)
    stock_actual_post = request.POST.get('stock_actual_inventario')
    stock_minimo_post = request.POST.get('stock_minimo_inventario')

    # Guardar valores previos para historial
    prev_stock_actual = inventario.stock_actual_inventario
    prev_stock_minimo = inventario.stock_minimo_inventario

    if stock_actual_post is not None and stock_actual_post != '':
        try:
            inventario.stock_actual_inventario = int(stock_actual_post)
        except (ValueError, TypeError):
            inventario.stock_actual_inventario = inventario.stock_actual_inventario

    if stock_minimo_post is not None and stock_minimo_post != '':
        try:
            inventario.stock_minimo_inventario = int(stock_minimo_post)
        except (ValueError, TypeError):
            inventario.stock_minimo_inventario = inventario.stock_minimo_inventario

    inventario.save()

    # Consolidar cambios de producto e inventario en un único HistorialInventario
    try:
        cambios = {}
        # stock
        if prev_stock_actual != inventario.stock_actual_inventario:
            cambios['stock_actual_inventario'] = [str(prev_stock_actual), str(inventario.stock_actual_inventario)]
        if prev_stock_minimo != inventario.stock_minimo_inventario:
            cambios['stock_minimo_inventario'] = [str(prev_stock_minimo), str(inventario.stock_minimo_inventario)]

        # producto: comparar con prev_product
        try:
            from decimal import Decimal, InvalidOperation
            campos_producto = ['nombre_producto', 'categoria_producto', 'modelo_producto', 'color_producto',
                               'capacidad_producto', 'descripcion_producto', 'precio_producto', 'codigo_barras_producto']
            for campo in campos_producto:
                antes = prev_product.get(campo)
                despues = getattr(producto, campo)

                if antes is None and despues is None:
                    continue

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
                        cambios[campo] = [format(antes_dec, 'f') if antes_dec is not None else None,
                                          format(despues_dec, 'f') if despues_dec is not None else None]
                    continue

                antes_s = str(antes) if antes is not None else None
                despues_s = str(despues) if despues is not None else None
                if antes_s != despues_s:
                    cambios[campo] = [antes_s, despues_s]
        except Exception:
            # No bloquear el flujo por errores en la comparación
            pass

        if cambios:
            import json
            HistorialInventario.objects.create(
                producto_id=producto.pk,
                nombre_producto=producto.nombre_producto or '',
                accion='edited',
                detalles=json.dumps(cambios, ensure_ascii=False),
            )
    except Exception:
        pass

    return redirect('inventario')

# ---------------------------------------------------------------------
# Eliminación de inventario (y producto relacionado)
# ---------------------------------------------------------------------
def eliminar_inventario_view(request, pk):
    """
    Elimina un registro de `Inventario` y (opcionalmente) el `Producto` relacionado.

    Comportamiento:
    - Solo procesa la eliminación cuando la petición es POST (más seguro).
    - Si se envía POST sin parámetros especiales: se elimina el `Inventario` y se intenta
      borrar el `Producto`. Si el `Producto` está referenciado por `DetalleFactura` (on_delete=PROTECT),
      no se eliminará y se informará al usuario.
    - Si se envía POST con el parámetro `force=1` (por ejemplo desde un formulario oculto),
      se realizará un borrado forzado: primero se eliminarán los `DetalleFactura` que referencian
      el producto y luego se eliminará el producto.

    Nota: borrar detalles de factura puede dejar inconsistencia en totales de facturas; úsalo con
    precaución. Recomendado: pedir confirmación en UI antes de usar `force`.
    """
    inventario = get_object_or_404(Inventario, pk=pk)
    producto = inventario.producto

    # Solo aceptar POST para borrar
    if request.method != 'POST':
        return redirect('inventario')

    # Determinar si el borrado debe ser forzado (eliminar detalles relacionados)
    force = str(request.POST.get('force', '')).lower() in ('1', 'true', 'yes')

    # Realizar operaciones dentro de una transacción atómica
    with transaction.atomic():
        # Eliminar primero el registro de inventario siempre
        inventario.delete()

        if force:
            # Borrado forzado: eliminar detalles que referencian el producto, luego el producto
            DetalleFactura.objects.filter(producto=producto).delete()
            producto.delete()
            messages.success(request, 'Inventario y producto eliminados (borrado forzado).')
            return redirect('inventario')

        # Intento de borrado normal; si está protegido, informar al usuario
        try:
            producto.delete()
            messages.success(request, 'Inventario y producto eliminados correctamente.')
        except ProtectedError:
            messages.warning(
                request,
                'Inventario eliminado. El producto no se pudo borrar porque está referenciado en facturas. Use borrado forzado si desea eliminar también los detalles.'
            )

    return redirect('inventario')

# ---------------------------------------------------------------------
# Búsqueda de producto via AJAX/JSON
# ---------------------------------------------------------------------
def buscar_producto(request):
    """
    Endpoint JSON para buscar un producto por código.
    - Parámetro GET: 'codigo'
    - Devuelve JSON con nombre, precio y stock o error 404 si no existe.
    Nota: nombres de campos usados según la implementación actual del modelo.
    """
    codigo = request.GET.get("codigo", "").strip()
    if not codigo:
        return JsonResponse({"error": "Código vacío"}, status=400)

    # Log mínimo para depuración (se puede reemplazar por logging)
    print("Código recibido:", codigo)

    try:
        # Ajustar nombre de campo si tu modelo usa distinto nombre (ej: codigo_barras_producto)
        producto = Producto.objects.get(codigo_barras=codigo)
        data = {
            "nombre": getattr(producto, 'nombre_producto', ''),
            "precio": float(getattr(producto, 'precio_producto', 0)),
            "stock": int(getattr(producto, 'stock_producto', 0))
        }
        print("Producto encontrado:", data)
        return JsonResponse(data, safe=True)

    except Producto.DoesNotExist:
        print("Producto NO encontrado")
        return JsonResponse({"error": "Producto no encontrado"}, status=404)


def historial_inventario_view(request):
    """
    Vista simple para mostrar el historial del inventario.
    Por ahora renderiza una plantilla estática similar a `inventario.html`.
    """
    from django.utils import timezone
    from .models import HistorialInventario

    # Soportar filtro por rango de fechas: fecha_inicial y fecha_final (formato YYYY-MM-DD)
    fecha_inicial = request.GET.get('fecha_inicial')
    fecha_final = request.GET.get('fecha_final')

    # Si no se proporcionan fechas en la query, por defecto usar el día actual
    if not fecha_inicial or not fecha_final:
        hoy = datetime.now().date()
        fecha_inicial = fecha_inicial or hoy.strftime('%Y-%m-%d')
        fecha_final = fecha_final or hoy.strftime('%Y-%m-%d')

    registros = HistorialInventario.objects.all()
    añadidos = registros.none()
    eliminados = registros.none()
    editados = registros.none()

    ventas = DetalleFactura.objects.none()
    # Intentar parsear las fechas (ahora siempre deberían existir) y filtrar
    try:
        di = datetime.strptime(fecha_inicial, '%Y-%m-%d').date()
        df = datetime.strptime(fecha_final, '%Y-%m-%d').date()
        if df < di:
            di, df = df, di

        # Filtrar registros del historial por rango
        registros = registros.filter(timestamp__date__range=[di, df])
        añadidos = registros.filter(accion='added')
        eliminados = registros.filter(accion='deleted')
        editados = registros.filter(accion='edited')

        # Consultar ventas (DetalleFactura) dentro del rango de fechas solicitado
        ventas = DetalleFactura.objects.select_related('producto', 'factura').filter(
            factura__fecha_factura__range=[di, df]
        ).order_by('-factura__fecha_factura', '-id')
    except Exception:
        # En caso de error de parseo, dejamos los QuerySets vacíos
        ventas = DetalleFactura.objects.none()

    # Convertir los detalles JSON de los registros editados a estructuras Python
    import json
    editados_lista = []
    try:
        for r in editados:
            modificaciones = {}
            if r.detalles:
                try:
                    modificaciones = json.loads(r.detalles)
                except Exception:
                    modificaciones = {}

            editados_lista.append({
                'producto_id': r.producto_id,
                'nombre_producto': r.nombre_producto,
                'timestamp': r.timestamp,
                'modificaciones': modificaciones,
                'historial_pk': r.pk,
            })
    except Exception:
        editados_lista = []

    context = {
        'añadidos': añadidos,
        'eliminados': eliminados,
        'editados': editados_lista,
        'ventas': ventas,
        'fecha_inicial': fecha_inicial or '',
        'fecha_final': fecha_final or '',
    }

    return render(request, 'productos/historial_inventario.html', context)


def detalle_producto_historial(request, pk):
    """
    Devuelve JSON con información para mostrar en un modal respecto a un registro de historial.
    Si el producto aún existe en la base, devuelve datos actuales del producto + inventario.
    Si no existe (p. ej. fue eliminado), devuelve el nombre guardado y el campo `detalles`.
    """
    from django.shortcuts import get_object_or_404

    historial = get_object_or_404(HistorialInventario, pk=pk)

    data = {
        'historial_id': historial.pk,
        'accion': historial.accion,
        'nombre_producto': historial.nombre_producto,
        'detalles': historial.detalles or '',
        'timestamp': historial.timestamp.isoformat(),
    }

    if historial.producto_id:
        try:
            producto = Producto.objects.get(id_producto=historial.producto_id)
            data.update({
                'producto_exists': True,
                'producto_id': producto.id_producto,
                'categoria_producto': producto.categoria_producto,
                'modelo_producto': producto.modelo_producto,
                'capacidad_producto': producto.capacidad_producto,
                'color_producto': producto.color_producto,
                'descripcion_producto': producto.descripcion_producto or '',
                'precio_producto': str(producto.precio_producto),
                'codigo_barras_producto': getattr(producto, 'codigo_barras_producto', ''),
                'imagen_url': producto.imagen_producto.url if producto.imagen_producto else None,
            })
            try:
                inventario = Inventario.objects.get(producto=producto)
                data['stock_actual_inventario'] = inventario.stock_actual_inventario
                data['stock_minimo_inventario'] = inventario.stock_minimo_inventario
            except Inventario.DoesNotExist:
                data['stock_actual_inventario'] = None
                data['stock_minimo_inventario'] = None
        except Producto.DoesNotExist:
            data['producto_exists'] = False
    else:
        data['producto_exists'] = False

    return JsonResponse(data)

