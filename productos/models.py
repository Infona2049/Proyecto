from django.db import models
from django.contrib.auth.models import AbstractUser 
import uuid

# Opciones para la categoría del producto
CATEGORIA_PRODUCTO_CHOICES = [
    ('Dispositivo', 'Dispositivo'),
    ('Auricular', 'Auricular'),
    ('Cargador', 'Cargador'),
]

# Opciones para el color del producto
COLOR_PRODUCTO_CHOICES = [
    ('negro', 'Negro'),
    ('blanco', 'Blanco'),
    ('dorado', 'Dorado'),
]

class Producto(models.Model):
    """
    Modelo que representa un producto en el sistema.
    """
    id_producto = models.AutoField(primary_key=True)  # ID autoincremental único
    nombre_producto = models.CharField(max_length=50)  # Nombre del producto
    categoria_producto = models.CharField(max_length=20, choices=CATEGORIA_PRODUCTO_CHOICES)  # Categoría con opciones limitadas
    modelo_producto = models.CharField(max_length=50)  # Modelo del producto
    capacidad_producto = models.CharField(
        max_length=20,
        choices=[('No Aplica', 'No Aplica'), ('128GB', '128GB'), ('256GB', '256GB'), ('512GB', '512GB')]
    )  # Capacidad con opciones limitadas
    color_producto = models.CharField(max_length=20, choices=COLOR_PRODUCTO_CHOICES)  # Color con opciones limitadas
    descripcion_producto = models.TextField(blank=True, null=True)  # Descripción opcional
    precio_producto = models.DecimalField(max_digits=10, decimal_places=2)  # Precio con dos decimales
    codigo_barras_producto = models.CharField(max_length=100, unique=True, blank=True)  # Código de barras único, puede generarse automáticamente
    iva_producto = models.DecimalField(max_digits=10, decimal_places=2, default=19.00, editable=False)  # IVA fijo al 19%, no editable
    imagen_producto = models.ImageField(upload_to='productos/', blank=True, null=True)  # Imagen opcional del producto

    def save(self, *args, **kwargs):
        """
        Sobrescribe el método save para:
        - Generar un código de barras único automáticamente si no se proporciona.
        - Asegurar que el IVA sea siempre 19.00.
        """
        if not self.codigo_barras_producto:
            # Genera un UUID, elimina guiones, toma los primeros 12 caracteres y los pone en mayúsculas
            self.codigo_barras_producto = str(uuid.uuid4()).replace('-', '')[:12].upper()
        
        self.iva_producto = 19.00  # Fija el IVA
        super().save(*args, **kwargs)

    def __str__(self):
        # Representación legible del producto
        return self.nombre_producto

class Inventario(models.Model):
    """
    Modelo que representa el inventario asociado a un producto.
    """
    id_inventario = models.AutoField(primary_key=True)  # ID autoincremental único
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)  # Relación con Producto, elimina inventario si se elimina el producto
    stock_actual_inventario = models.IntegerField(default=0)  # Cantidad actual en stock
    stock_minimo_inventario = models.IntegerField(default=1)  # Stock mínimo permitido antes de alerta
    fecha_actualizacion_inventario = models.DateTimeField(auto_now=True)  # Fecha y hora de la última actualización automática
    codigo_barras_inventario = models.CharField(max_length=100, unique=True)  # Código de barras único para inventario (normalmente igual al producto)
    imagen_inventario = models.ImageField(upload_to='inventario/', blank=True, null=True)  # Imagen opcional para inventario

    def __str__(self):
        # Representación legible del inventario mostrando producto y stock actual
        return f"{self.producto.nombre_producto} - Stock: {self.stock_actual_inventario}"