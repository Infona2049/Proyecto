from django.contrib import admin # importa el modulo de administración de django
from .models import Factura # importa el modelo de factura desde el archivo models.py

@admin.register(Factura) # registra el modelo de factura en el admin de django
class FacturaAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'nombre_emisor',   
        'nit_emisor',      
        'nombre_receptor',
        'nit_receptor',
        'correo_cliente',
        'telefono',
        'fecha_factura',
        'metodo_pago_factura',
        'total_factura',
        'estado',
    )
    list_filter = ('estado', 'metodo_pago_factura', 'fecha_factura')
    search_fields = ('nombre_receptor', 'correo_cliente', 'nit_receptor', 'cufe_factura')
    date_hierarchy = 'fecha_factura'
    ordering = ('-fecha_factura',)