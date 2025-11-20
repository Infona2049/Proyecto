from django.http import JsonResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from .models import Inventario, Producto
from .forms import ProductoForm
import json

@csrf_exempt
def inventario_api(request, id):
    try:
        inventario = Inventario.objects.select_related('producto').get(id_inventario=id)
    except Inventario.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'No encontrado'}, status=404)

    if request.method == 'GET':
        # Devolver datos del producto e inventario
        data = {
            'nombre_producto': inventario.producto.nombre_producto,
            'categoria_producto': inventario.producto.categoria_producto,
            'modelo_producto': inventario.producto.modelo_producto,
            'color_producto': inventario.producto.color_producto,
            'capacidad_producto': inventario.producto.capacidad_producto,
            'precio_producto': float(inventario.producto.precio_producto),
            'stock_actual': inventario.stock_actual_inventario,
        }
        return JsonResponse(data)

    elif request.method == 'PUT':
        # Actualizar producto e inventario
        data = request.POST or json.loads(request.body.decode())
        form = ProductoForm(data, instance=inventario.producto)
        if form.is_valid():
            producto = form.save()
            stock_actual = int(data.get('stock_actual', inventario.stock_actual_inventario))
            inventario.stock_actual_inventario = stock_actual
            inventario.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': form.errors.as_json()}, status=400)

    elif request.method == 'DELETE':
        inventario.producto.delete()
        inventario.delete()
        return JsonResponse({'success': True})

    return HttpResponseNotAllowed(['GET', 'PUT', 'DELETE'])
