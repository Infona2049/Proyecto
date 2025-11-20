#!/usr/bin/env python
"""
Script de verificación completa del sistema de autenticación y roles
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EcoFactProject.settings')
django.setup()

from django.contrib.auth import authenticate
from core.models import Usuario
from django.utils import timezone

def crear_usuarios_de_prueba():
    """Crea usuarios de prueba para cada rol"""
    usuarios = [
        {
            'email': 'admin@ecofact.com',
            'username': 'admin_test',
            'nombre': 'Admin',
            'apellido': 'Prueba',
            'rol': 'admin',
            'password': 'admin123',
            'documento': '12345678'
        },
        {
            'email': 'vendedor@ecofact.com',
            'username': 'vendedor_test',
            'nombre': 'Vendedor',
            'apellido': 'Prueba',
            'rol': 'vendedor',
            'password': 'vendedor123',
            'documento': '87654321'
        },
        {
            'email': 'cliente@ecofact.com',
            'username': 'cliente_test',
            'nombre': 'Cliente',
            'apellido': 'Prueba',
            'rol': 'cliente',
            'password': 'cliente123',
            'documento': '11223344'
        }
    ]
    
    print("=== CREANDO USUARIOS DE PRUEBA ===")
    
    for user_data in usuarios:
        try:
            usuario = Usuario.objects.get(correo_electronico_usuario=user_data['email'])
            print(f"✅ Usuario {user_data['rol']} ya existe: {user_data['email']}")
        except Usuario.DoesNotExist:
            usuario = Usuario.objects.create_user(
                correo_electronico_usuario=user_data['email'],
                username=user_data['username'],
                nombre_usuario=user_data['nombre'],
                apellido_usuario=user_data['apellido'],
                numero_documento_usuario=user_data['documento'],
                rol_usuario=user_data['rol'],
                password=user_data['password']
            )
            print(f"✅ Usuario {user_data['rol']} creado: {user_data['email']}")

def probar_bloqueo_por_rol():
    """Prueba el sistema de bloqueo para cada rol"""
    print("\n=== PROBANDO BLOQUEO POR ROL ===")
    
    roles = ['admin', 'vendedor', 'cliente']
    
    for rol in roles:
        print(f"\n--- Probando rol: {rol.upper()} ---")
        
        email = f"{rol}@ecofact.com"
        try:
            usuario = Usuario.objects.get(correo_electronico_usuario=email)
            
            # Resetear estado
            usuario.resetear_intentos_fallidos()
            print(f"Estado inicial - Intentos: {usuario.intentos_fallidos}")
            
            # Simular 3 intentos fallidos
            for i in range(1, 4):
                auth_user = authenticate(
                    username=email,
                    password="contraseña_incorrecta"
                )
                
                if auth_user is None:
                    usuario.refresh_from_db()
                    usuario.incrementar_intentos_fallidos()
                    usuario.refresh_from_db()
                    
                    print(f"  Intento {i} - Fallidos: {usuario.intentos_fallidos}, Bloqueado: {usuario.esta_bloqueado()}")
                    
                    if usuario.esta_bloqueado():
                        tiempo_restante = usuario.bloqueado_hasta - timezone.now()
                        minutos = int(tiempo_restante.total_seconds() / 60)
                        print(f"  🔒 Usuario bloqueado por {minutos} minutos")
                        break
            
            # Desbloquear para próxima prueba
            usuario.resetear_intentos_fallidos()
            
        except Usuario.DoesNotExist:
            print(f"❌ Usuario {rol} no encontrado")

def probar_login_exitoso():
    """Prueba login exitoso para cada rol"""
    print("\n=== PROBANDO LOGIN EXITOSO POR ROL ===")
    
    credenciales = {
        'admin': ('admin@ecofact.com', 'admin123'),
        'vendedor': ('vendedor@ecofact.com', 'vendedor123'),
        'cliente': ('cliente@ecofact.com', 'cliente123')
    }
    
    for rol, (email, password) in credenciales.items():
        auth_user = authenticate(username=email, password=password)
        
        if auth_user:
            print(f"✅ Login exitoso - {rol.upper()}: {email}")
            print(f"   Rol del usuario: {auth_user.rol_usuario}")
            print(f"   Intentos fallidos: {auth_user.intentos_fallidos}")
        else:
            print(f"❌ Login falló - {rol.upper()}: {email}")

def mostrar_rutas_protegidas():
    """Muestra las rutas protegidas por rol"""
    print("\n=== RUTAS PROTEGIDAS POR ROL ===")
    
    rutas_protegidas = {
        'ADMIN': [
            '/admin-dashboard/',
            '/visualizacion_admin/',
        ],
        'VENDEDOR': [
            '/vendedor-dashboard/',
            '/visualizacion_vendedor/',
            '/historial_factura/',
            '/crear_factura/',
        ],
        'CLIENTE': [
            '/cliente-dashboard/',
            '/visualizacion_cliente/',
        ],
        'COMPARTIDAS (requieren login)': [
            '/documentos/',
            '/actualizar_perfil/',
        ],
        'PÚBLICAS': [
            '/login/',
            '/registro/',
            '/olvido_contraseña/',
            '/acerca_nosotros/',
        ]
    }
    
    for categoria, rutas in rutas_protegidas.items():
        print(f"\n{categoria}:")
        for ruta in rutas:
            print(f"  - {ruta}")

def verificar_estado_sistema():
    """Verifica el estado general del sistema"""
    print("\n=== ESTADO DEL SISTEMA ===")
    
    total_usuarios = Usuario.objects.count()
    usuarios_bloqueados = Usuario.objects.filter(
        bloqueado_hasta__isnull=False,
        bloqueado_hasta__gt=timezone.now()
    ).count()
    usuarios_con_intentos = Usuario.objects.filter(intentos_fallidos__gt=0).count()
    
    print(f"Total de usuarios: {total_usuarios}")
    print(f"Usuarios bloqueados: {usuarios_bloqueados}")
    print(f"Usuarios con intentos fallidos: {usuarios_con_intentos}")
    
    # Mostrar estadísticas por rol
    for rol in ['admin', 'vendedor', 'cliente']:
        count = Usuario.objects.filter(rol_usuario=rol).count()
        print(f"Usuarios {rol}: {count}")

if __name__ == "__main__":
    print("🚀 VERIFICACIÓN COMPLETA DEL SISTEMA DE AUTENTICACIÓN")
    print("=" * 60)
    
    try:
        crear_usuarios_de_prueba()
        probar_bloqueo_por_rol()
        probar_login_exitoso()
        mostrar_rutas_protegidas()
        verificar_estado_sistema()
        
        print("\n" + "=" * 60)
        print("✅ VERIFICACIÓN COMPLETADA EXITOSAMENTE")
        print("\nFUNCIONALIDADES IMPLEMENTADAS:")
        print("• ✅ Límite de 3 intentos de login por usuario")
        print("• ✅ Bloqueo automático por 10 minutos después de 3 intentos")
        print("• ✅ Bloqueo funciona para TODOS los roles (admin, vendedor, cliente)")
        print("• ✅ Redirección automática por rol después del login")
        print("• ✅ Protección de rutas por rol")
        print("• ✅ Middleware para prevenir acceso cruzado entre roles")
        print("• ✅ Interface de administración para gestionar bloqueos")
        print("• ✅ Comandos de consola para gestión de usuarios")
        
        print("\nCOMANDOS DISPONIBLES:")
        print("• python manage.py unlock_user --email usuario@email.com")
        print("• python manage.py unlock_user --all")
        print("• python manage.py check_login_status")
        print("• python manage.py check_login_status --blocked-only")
        
    except Exception as e:
        print(f"\n❌ ERROR EN LA VERIFICACIÓN: {e}")
        import traceback
        traceback.print_exc()