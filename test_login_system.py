#!/usr/bin/env python
"""
Script de prueba para el sistema de control de intentos de login
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

def crear_usuario_prueba():
    """Crea un usuario de prueba si no existe"""
    email = "test@ecofact.com"
    try:
        usuario = Usuario.objects.get(correo_electronico_usuario=email)
        print(f"✅ Usuario de prueba ya existe: {email}")
    except Usuario.DoesNotExist:
        usuario = Usuario.objects.create_user(
            correo_electronico_usuario=email,
            username="testuser",
            nombre_usuario="Test",
            apellido_usuario="User",
            rol_usuario="cliente",
            password="test123"
        )
        print(f"✅ Usuario de prueba creado: {email}")
    
    return usuario

def probar_intentos_fallidos():
    """Prueba el sistema de intentos fallidos"""
    print("\n=== PRUEBA DE INTENTOS FALLIDOS ===")
    
    usuario = crear_usuario_prueba()
    
    # Resetear estado inicial
    usuario.resetear_intentos_fallidos()
    print(f"Estado inicial - Intentos: {usuario.intentos_fallidos}, Bloqueado: {usuario.esta_bloqueado()}")
    
    # Simular 3 intentos fallidos
    for i in range(1, 4):
        # Intentar autenticar con contraseña incorrecta
        auth_user = authenticate(
            username=usuario.correo_electronico_usuario, 
            password="contraseña_incorrecta"
        )
        
        if auth_user is None:
            usuario.refresh_from_db()
            usuario.incrementar_intentos_fallidos()
            usuario.refresh_from_db()
            
            print(f"Intento {i} fallido - Intentos acumulados: {usuario.intentos_fallidos}")
            print(f"  ¿Está bloqueado?: {usuario.esta_bloqueado()}")
            
            if usuario.bloqueado_hasta:
                tiempo_restante = usuario.bloqueado_hasta - timezone.now()
                minutos = int(tiempo_restante.total_seconds() / 60)
                print(f"  Bloqueado hasta: {usuario.bloqueado_hasta} ({minutos} minutos)")
    
    return usuario

def probar_desbloqueo():
    """Prueba el desbloqueo manual"""
    print("\n=== PRUEBA DE DESBLOQUEO ===")
    
    usuario = crear_usuario_prueba()
    
    if usuario.esta_bloqueado():
        print(f"Usuario bloqueado. Desbloqueando...")
        usuario.resetear_intentos_fallidos()
        print(f"✅ Usuario desbloqueado. Intentos: {usuario.intentos_fallidos}")
    else:
        print("ℹ️ Usuario no estaba bloqueado")

def probar_login_exitoso():
    """Prueba un login exitoso después del bloqueo"""
    print("\n=== PRUEBA DE LOGIN EXITOSO ===")
    
    usuario = crear_usuario_prueba()
    
    # Asegurar que el usuario esté desbloqueado
    usuario.resetear_intentos_fallidos()
    
    # Intentar login exitoso
    auth_user = authenticate(
        username=usuario.correo_electronico_usuario,
        password="test123"
    )
    
    if auth_user:
        usuario.refresh_from_db()
        usuario.resetear_intentos_fallidos()
        print(f"✅ Login exitoso - Intentos reseteados: {usuario.intentos_fallidos}")
    else:
        print("❌ Login falló")

def mostrar_estado_usuarios():
    """Muestra el estado de todos los usuarios con intentos fallidos"""
    print("\n=== ESTADO DE USUARIOS ===")
    
    usuarios_con_intentos = Usuario.objects.filter(intentos_fallidos__gt=0)
    
    if usuarios_con_intentos.exists():
        for usuario in usuarios_con_intentos:
            estado = "🔒 BLOQUEADO" if usuario.esta_bloqueado() else "⚠️ CON INTENTOS"
            print(f"{estado} {usuario.correo_electronico_usuario}")
            print(f"  Intentos: {usuario.intentos_fallidos}")
            print(f"  Último intento: {usuario.ultimo_intento_fallido}")
            print(f"  Bloqueado hasta: {usuario.bloqueado_hasta}")
            print()
    else:
        print("✅ No hay usuarios con intentos fallidos")

if __name__ == "__main__":
    print("🚀 INICIANDO PRUEBAS DEL SISTEMA DE LOGIN")
    
    try:
        # Ejecutar todas las pruebas
        probar_intentos_fallidos()
        probar_desbloqueo()
        probar_login_exitoso()
        mostrar_estado_usuarios()
        
        print("\n✅ TODAS LAS PRUEBAS COMPLETADAS")
        
    except Exception as e:
        print(f"\n❌ ERROR EN LAS PRUEBAS: {e}")
        import traceback
        traceback.print_exc()