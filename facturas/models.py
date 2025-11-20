from django.db import models# importa el modulo de modelos de django
from datetime import date # importa la clase date para manejar fechas
from core.models import Usuario # importa el modelo de usuario para poder relacionar con historial de factura
from productos.models import Producto  # importa el modelo  de productos para poder relacionar con detalle de factura


# Opciones del historial 
EVENTO_HISTORIAL_CHOICES = [ # opciones para el historial de factura
    ("CREADA", "Factura creada"),
    ("ACTUALIZADA", "Factura actualizada"),
    ("ELIMINADA", "Factura eliminada"),
    ("ENVIADA", "Factura enviada"),
]


# MODELO DE FACTURA
class Factura(models.Model): 
    id = models.BigAutoField(primary_key=True) # ID auto incremental 
    nombre_emisor = models.CharField(max_length=255, default="Apple S.A.S") # nombre del emisor de la factura
    nit_emisor = models.CharField(max_length=50, default="4587128-141") # nit del emisor de la factura
    nombre_receptor = models.CharField(max_length=255) # nombre del receptor de la factura
    nit_receptor = models.CharField(max_length=50) # nit del receptor de la factura
    correo_cliente = models.EmailField() # correo electrónico del cliente
    telefono = models.CharField(max_length=20, blank=True, null=True) # teléfono del cliente
    direccion = models.CharField(max_length=255, blank=True, null=True) # dirección del cliente
    estado = models.CharField(max_length=30, default="Pendiente") # estado de la factura
    fecha = models.DateField(default=date.today) # fecha de creación de la factura
    fecha_factura = models.DateField(default=date.today) # fecha de la factura
    hora_expedicion = models.TimeField(auto_now_add=True, null=True, blank=True) # hora de expedición de la factura
    metodo_pago_factura = models.CharField(max_length=15) # método de pago de la factura
    cufe_factura = models.CharField(max_length=255, unique=True, default="TEMP") # CUFE de la factura
    sutotal_factura = models.DecimalField(max_digits=10, decimal_places=2, default=0) # subtotal de la factura
    iva_total_factura = models.DecimalField(max_digits=10, decimal_places=2, default=0) # IVA total de la factura
    total_factura = models.DecimalField(max_digits=10, decimal_places=2, default=0) # total de la factura
    cliente_id = models.IntegerField(default=1) # ID del cliente

    class Meta: 
        db_table = "facturas_factura"

    def __str__(self): 
        return f"Factura {self.id} - {self.nombre_receptor}"


# MODELO DE DETALLE DE FACTURA
class DetalleFactura(models.Model):
    factura = models.ForeignKey(Factura, related_name="detalles", on_delete=models.CASCADE) # relación con la factura
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)  # relación con inventario de productos
    cantidad = models.IntegerField() # cantidad del producto
    precio = models.DecimalField(max_digits=12, decimal_places=2) # precio del producto
    iva = models.DecimalField(max_digits=12, decimal_places=2, default=0) # IVA del producto
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0) # total del producto

    def __str__(self):
        return f"{self.producto} (x{self.cantidad}) - Factura {self.factura.id}"


# MODELO DE HISTORIAL DE FACTURA
class HistorialFactura(models.Model): 
    id_historial_factura = models.AutoField(primary_key=True)# ID auto incremental del historial de factura
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE) # relación con la factura
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE) # relación con el usuario
    fecha_de_evento = models.DateTimeField(auto_now_add=True) # fecha y hora del evento
    evento_historial_factura = models.CharField(max_length=20, choices=EVENTO_HISTORIAL_CHOICES) # tipo de evento
    observacion_historial_factura = models.TextField(blank=True, null=True) # observaciones del evento
    def __str__(self):  
        return f"Historial {self.id_historial_factura} - Factura {self.factura.id}"
