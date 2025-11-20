#!/usr/bin/env python
import os
import sys
import django

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EcoFactProject.settings')
django.setup()

from core.models import Usuario

def create_test_users():
    print("🔧 Creando usuarios de prueba...")
    
    # Usuario administrador
    if not Usuario.objects.filter(username='admin').exists():
        admin = Usuario.objects.create_user(
            username='admin',
            correo_electronico_usuario='admin@ecofact.com',
            password='admin123',
            nombre_usuario='Admin',
            apellido_usuario='Sistema',
            numero_documento_usuario='12345678',
            rol_usuario='admin'
        )
        print(f"✅ Usuario administrador creado: {admin.correo_electronico_usuario}")
    else:
        print("⚠️  Usuario administrador ya existe")

    # Usuario vendedor
    if not Usuario.objects.filter(username='vendedor').exists():
        vendedor = Usuario.objects.create_user(
            username='vendedor',
            correo_electronico_usuario='vendedor@ecofact.com',
            password='vendedor123',
            nombre_usuario='Juan',
            apellido_usuario='Vendedor',
            numero_documento_usuario='87654321',
            rol_usuario='vendedor'
        )
        print(f"✅ Usuario vendedor creado: {vendedor.correo_electronico_usuario}")
    else:
        print("⚠️  Usuario vendedor ya existe")

    # Usuario cliente
    if not Usuario.objects.filter(username='cliente').exists():
        cliente = Usuario.objects.create_user(
            username='cliente',
            correo_electronico_usuario='cliente@ecofact.com',
            password='cliente123',
            nombre_usuario='María',
            apellido_usuario='Cliente',
            numero_documento_usuario='11223344',
            rol_usuario='cliente'
        )
        print(f"✅ Usuario cliente creado: {cliente.correo_electronico_usuario}")
    else:
        print("⚠️  Usuario cliente ya existe")

    print("\n🎉 Proceso completado!")
    print("\n📋 Credenciales de acceso:")
    print("👑 Admin: admin@ecofact.com / admin123")
    print("💼 Vendedor: vendedor@ecofact.com / vendedor123") 
    print("👤 Cliente: cliente@ecofact.com / cliente123")
    
    print(f"\n📊 Total de usuarios en el sistema: {Usuario.objects.count()}")

if __name__ == '__main__':
    try:
        create_test_users()
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Asegúrate de que las migraciones estén aplicadas:")
        print("   python manage.py makemigrations")
        print("   python manage.py migrate")