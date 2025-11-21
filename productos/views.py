# ...existing code...
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.core.paginator import Paginator
from django.contrib import messages
from django.db import transaction
from django.db.models.deletion import ProtectedError

# importar modelo DetalleFactura para borrado forzado de referencias
from facturas.models import DetalleFactura

# Importar modelos y formularios del mismo app
from .models import Inventario, Producto
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

    producto.save()

    # Actualizar campos de inventario (intentar convertir a int si procede)
    stock_actual = request.POST.get('stock_actual_inventario')
    if stock_actual is not None and stock_actual != '':
        try:
            inventario.stock_actual_inventario = int(stock_actual)
        except (ValueError, TypeError):
            inventario.stock_actual_inventario = inventario.stock_actual_inventario

    stock_minimo = request.POST.get('stock_minimo_inventario')
    if stock_minimo is not None and stock_minimo != '':
        try:
            inventario.stock_minimo_inventario = int(stock_minimo)
        except (ValueError, TypeError):
            inventario.stock_minimo_inventario = inventario.stock_minimo_inventario

    inventario.save()
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
