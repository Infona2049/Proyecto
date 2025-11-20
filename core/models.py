from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta
import uuid
from productos.models import Producto


# Opciones para ENUM
TIPO_DOCUMENTO_CHOICES = [
    ('cc', 'Cédula de ciudadanía'),
    ('ce', 'Cédula de extranjería'),
    ('pa', 'Pasaporte'),
    ('ppt', 'Permiso por protección temporal'),
    ('nit', 'NIT'),
    ('cif', 'CIF'),
    ('ruc', 'RUC'),
]

ROL_USUARIO_CHOICES = [
    ('admin', 'Administrador'),
    ('vendedor', 'Vendedor'),
    ('cliente', 'Cliente'),
]

METODO_PAGO_CHOICES = [
    ('Efectivo', 'Efectivo'),
    ('Tarjeta', 'Tarjeta'),
    ('Transferencia', 'Transferencia'),
]

EVENTO_HISTORIAL_CHOICES = [
    ('pendiente', 'Pendiente'),
    ('aprobada', 'Aprobada'),
    ('rechazada', 'Rechazada'),
]

REGIMEN_EMPRESA_CHOICES = [
    ('Simplificado', 'Simplificado'),
    ('Comun', 'Común'),
    ('Especial', 'Especial'),
]

class Usuario(AbstractUser):
    id_usuario = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True, null=False, blank=False)
    nombre_usuario = models.CharField(max_length=30)
    segundo_nombre_usuario = models.CharField(max_length=30, blank=True, null=True)
    apellido_usuario = models.CharField(max_length=30)
    segundo_apellido_usuario = models.CharField(max_length=30, blank=True, null=True)
    tipo_documento_usuario = models.CharField(max_length=5, choices=TIPO_DOCUMENTO_CHOICES, default='cc')
    numero_documento_usuario = models.CharField(max_length=15, unique=True)
    correo_electronico_usuario = models.EmailField(max_length=100, unique=True)
    direccion_usuario = models.CharField(max_length=100, blank=True, null=True)
    telefono_usuario = models.CharField(max_length=15, blank=True, null=True)
    rol_usuario = models.CharField(max_length=10, choices=ROL_USUARIO_CHOICES)
    fecha_creacion_usuario = models.DateTimeField(auto_now_add=True)
    
    # Campos para control de intentos de login
    intentos_fallidos = models.IntegerField(default=0)
    bloqueado_hasta = models.DateTimeField(null=True, blank=True)
    ultimo_intento_fallido = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'correo_electronico_usuario'
    REQUIRED_FIELDS = ['username', 'nombre_usuario', 'apellido_usuario', 'rol_usuario']

    def _str_(self):
        return self.correo_electronico_usuario
    
    def esta_bloqueado(self):
        """Verifica si el usuario está bloqueado por intentos fallidos"""
        if self.bloqueado_hasta and timezone.now() < self.bloqueado_hasta:
            return True
        elif self.bloqueado_hasta and timezone.now() >= self.bloqueado_hasta:
            # Si el tiempo de bloqueo ya pasó, resetear intentos
            self.intentos_fallidos = 0
            self.bloqueado_hasta = None
            self.save()
        return False
    
    def incrementar_intentos_fallidos(self):
        """Incrementa los intentos fallidos y bloquea si es necesario"""
        self.intentos_fallidos += 1
        self.ultimo_intento_fallido = timezone.now()
        
        if self.intentos_fallidos >= 3:
            # Bloquear por 10 minutos
            self.bloqueado_hasta = timezone.now() + timedelta(minutes=10)
        
        self.save()
    
    def resetear_intentos_fallidos(self):
        """Resetea los intentos fallidos después de un login exitoso"""
        self.intentos_fallidos = 0
        self.bloqueado_hasta = None
        self.ultimo_intento_fallido = None
        self.save()

class Empresa(models.Model):
    id_empresa = models.AutoField(primary_key=True)
    nombre_empresa = models.CharField(max_length=100)
    nit_empresa = models.CharField(max_length=15, unique=True)
    direccion_empresa = models.CharField(max_length=150)
    telefono_empresa = models.CharField(max_length=15)
    correo_empresa = models.EmailField(max_length=100)
    regimen_empresa = models.CharField(max_length=15, choices=REGIMEN_EMPRESA_CHOICES, default='Comun')
    representante_legal = models.CharField(max_length=100)
    fecha_creacion_empresa = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return self.nombre_empresa




