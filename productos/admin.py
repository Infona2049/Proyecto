from django.contrib import admin
from .models import (
    Inventario,
    Producto
)

# Registro y configuración del modelo Producto en el admin de Django
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    # Campos que se mostrarán en la lista de productos en el admin
    list_display = (
        'id_producto',
        'nombre_producto',
        'categoria_producto',
        'modelo_producto',
        'capacidad_producto',
        'color_producto',
        'precio_producto',
        'codigo_barras_producto',
    )
    # Filtros laterales para facilitar la búsqueda por estas características
    list_filter = ('categoria_producto', 'color_producto', 'modelo_producto', 'capacidad_producto')
    # Campos que se pueden buscar mediante la barra de búsqueda
    search_fields = ('nombre_producto', 'modelo_producto', 'codigo_barras_producto')
    # Orden predeterminado de los productos (por id ascendente)
    ordering = ('id_producto',)

# Registro y configuración del modelo Inventario en el admin de Django
@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):
    # Campos que se mostrarán en la lista de inventarios en el admin
    list_display = (
        'id_inventario',
        'producto',  # Muestra el producto relacionado
        'stock_actual_inventario',
        'stock_minimo_inventario',
        'fecha_actualizacion_inventario',
        'codigo_barras_inventario',
    )
    # Filtro lateral para buscar inventarios por producto
    list_filter = ('producto',)
    # Campos que se pueden buscar, incluyendo el nombre del producto relacionado
    search_fields = ('producto__nombre_producto', 'codigo_barras_inventario')
    # Orden predeterminado: mostrar primero los inventarios más recientes
    ordering = ('-fecha_actualizacion_inventario',)