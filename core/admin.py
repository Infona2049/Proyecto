from django.contrib import admin
from django.utils import timezone
from django.contrib import messages
from .models import (
    Usuario,
    Empresa,

)
# Se cambió el import del modelo DetalleFactura, ahora se importa desde facturas.models
from facturas.models import DetalleFactura 
from facturas.models import HistorialFactura 

# --- FUNCIONES AUXILIARES PARA ADMIN ---
def desbloquear_usuarios_seleccionados(modeladmin, request, queryset):
    """Acción para desbloquear usuarios seleccionados"""
    count = 0
    for usuario in queryset:
        if usuario.esta_bloqueado():
            usuario.resetear_intentos_fallidos()
            count += 1
    
    if count > 0:
        messages.success(request, f'Se desbloquearon {count} usuarios.')
    else:
        messages.info(request, 'Ningún usuario estaba bloqueado.')

desbloquear_usuarios_seleccionados.short_description = "Desbloquear usuarios seleccionados"

def resetear_intentos_fallidos(modeladmin, request, queryset):
    """Acción para resetear intentos fallidos de usuarios seleccionados"""
    queryset.update(
        intentos_fallidos=0,
        bloqueado_hasta=None,
        ultimo_intento_fallido=None
    )
    messages.success(request, f'Se resetearon los intentos de {queryset.count()} usuarios.')

resetear_intentos_fallidos.short_description = "Resetear intentos fallidos"  

# --- MODELO USUARIO ---
@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = (
        'id_usuario',
        'username',
        'nombre_usuario',
        'apellido_usuario',
        'correo_electronico_usuario',
        'rol_usuario',
        'intentos_fallidos',
        'estado_bloqueo',
        'fecha_creacion_usuario',
    )
    list_filter = ('rol_usuario', 'tipo_documento_usuario', 'intentos_fallidos')
    search_fields = (
        'username',
        'nombre_usuario',
        'apellido_usuario',
        'correo_electronico_usuario',
        'numero_documento_usuario',
    )
    ordering = ('id_usuario',)
    actions = [desbloquear_usuarios_seleccionados, resetear_intentos_fallidos]
    
    # Campos de solo lectura para mostrar información del bloqueo y fechas no editables
    readonly_fields = ('estado_bloqueo', 'tiempo_restante_bloqueo', 'fecha_creacion_usuario', 'last_login', 'date_joined')
    
    def estado_bloqueo(self, obj):
        """Muestra el estado de bloqueo del usuario"""
        if obj.esta_bloqueado():
            return "🔒 BLOQUEADO"
        elif obj.intentos_fallidos > 0:
            return f"⚠️ {obj.intentos_fallidos} intentos fallidos"
        else:
            return "✅ Sin problemas"
    estado_bloqueo.short_description = "Estado de Bloqueo"
    
    def tiempo_restante_bloqueo(self, obj):
        """Muestra el tiempo restante de bloqueo"""
        if obj.esta_bloqueado() and obj.bloqueado_hasta:
            tiempo_restante = obj.bloqueado_hasta - timezone.now()
            minutos = int(tiempo_restante.total_seconds() / 60)
            return f"{minutos} minutos restantes"
        return "No aplica"
    tiempo_restante_bloqueo.short_description = "Tiempo Restante"
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('username', 'nombre_usuario', 'segundo_nombre_usuario', 
                      'apellido_usuario', 'segundo_apellido_usuario')
        }),
        ('Documento y Contacto', {
            'fields': ('tipo_documento_usuario', 'numero_documento_usuario', 
                      'correo_electronico_usuario', 'direccion_usuario', 'telefono_usuario')
        }),
        ('Configuración de Cuenta', {
            'fields': ('rol_usuario', 'password')
        }),
        ('Control de Intentos de Login', {
            'fields': ('intentos_fallidos', 'ultimo_intento_fallido', 'bloqueado_hasta',
                      'estado_bloqueo', 'tiempo_restante_bloqueo'),
            'classes': ('collapse',),
        }),
        ('Fechas Importantes', {
            'fields': ('fecha_creacion_usuario', 'last_login', 'date_joined'),
            'classes': ('collapse',),
        }),
    )


# --- MODELO EMPRESA ---
@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = (
        'id_empresa',
        'nombre_empresa',
        'nit_empresa',
        'regimen_empresa',
        'representante_legal',
        'fecha_creacion_empresa',
    )
    list_filter = ('regimen_empresa',)
    search_fields = ('nombre_empresa', 'nit_empresa', 'representante_legal')
    ordering = ('id_empresa',)


# --- MODELO DETALLE FACTURA ---
@admin.register(DetalleFactura)
class DetalleFacturaAdmin(admin.ModelAdmin):
    list_display = (
       'id',
       'factura',
       'producto',
       'cantidad',
        'precio',
       'iva',
      'total',
)
list_filter = ('producto',)
search_fields = ('producto', 'factura__cufe_factura')
ordering = ('id',)



# --- MODELO HISTORIAL FACTURA ---
@admin.register(HistorialFactura)
class HistorialFacturaAdmin(admin.ModelAdmin):
    list_display = (
        'id_historial_factura',
        'factura',
        'usuario',
        'fecha_de_evento',
        'evento_historial_factura',
        'observacion_historial_factura',
    )
    list_filter = ('evento_historial_factura', 'fecha_de_evento')
    search_fields = ('factura__cufe_factura', 'usuario__correo_electronico_usuario')
    date_hierarchy = 'fecha_de_evento'
    ordering = ('-fecha_de_evento',)
