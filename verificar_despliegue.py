#!/usr/bin/env python
"""
Script de verificación pre-despliegue para Render
Verifica que todo esté listo antes de desplegar
"""

import os
import sys
from pathlib import Path

def check_file_exists(file_path, description):
    """Verifica si un archivo existe"""
    if Path(file_path).exists():
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description} NO ENCONTRADO: {file_path}")
        return False

def check_requirements():
    """Verifica el archivo requirements.txt"""
    required_packages = ['gunicorn', 'whitenoise', 'dj-database-url', 'psycopg2']
    
    try:
        with open('requirements.txt', 'r') as f:
            content = f.read().lower()
            missing = []
            for package in required_packages:
                if package not in content:
                    missing.append(package)
            
            if not missing:
                print(f"✅ requirements.txt contiene todos los paquetes necesarios")
                return True
            else:
                print(f"❌ Faltan paquetes en requirements.txt: {', '.join(missing)}")
                return False
    except FileNotFoundError:
        print("❌ requirements.txt no encontrado")
        return False

def check_settings():
    """Verifica configuraciones en settings.py"""
    checks_passed = True
    
    try:
        with open('EcoFactProject/settings.py', 'r') as f:
            content = f.read()
            
            # Verificar imports necesarios
            required_imports = [
                ('dj_database_url', 'import dj_database_url'),
                ('whitenoise', 'whitenoise')
            ]
            
            for package, import_statement in required_imports:
                if import_statement in content:
                    print(f"✅ settings.py importa {package}")
                else:
                    print(f"❌ settings.py NO importa {package}")
                    checks_passed = False
            
            # Verificar configuraciones
            if 'ALLOWED_HOSTS' in content:
                print(f"✅ ALLOWED_HOSTS está configurado")
            else:
                print(f"❌ ALLOWED_HOSTS no está configurado")
                checks_passed = False
            
            if 'WhiteNoiseMiddleware' in content:
                print(f"✅ WhiteNoise middleware está configurado")
            else:
                print(f"❌ WhiteNoise middleware NO está configurado")
                checks_passed = False
            
            if 'DATABASE_URL' in content:
                print(f"✅ Configuración para DATABASE_URL encontrada")
            else:
                print(f"⚠️  DATABASE_URL no mencionado (verificar manualmente)")
            
            return checks_passed
            
    except FileNotFoundError:
        print("❌ settings.py no encontrado")
        return False

def check_build_script():
    """Verifica el script build.sh"""
    try:
        with open('build.sh', 'r') as f:
            content = f.read()
            
            required_commands = [
                ('pip install', 'Instalación de dependencias'),
                ('collectstatic', 'Recolección de archivos estáticos'),
                ('migrate', 'Migraciones de base de datos')
            ]
            
            checks_passed = True
            for command, description in required_commands:
                if command in content:
                    print(f"✅ build.sh incluye: {description}")
                else:
                    print(f"❌ build.sh NO incluye: {description}")
                    checks_passed = False
            
            return checks_passed
    except FileNotFoundError:
        print("❌ build.sh no encontrado")
        return False

def main():
    """Función principal"""
    print("=" * 60)
    print("🔍 VERIFICACIÓN PRE-DESPLIEGUE PARA RENDER")
    print("=" * 60)
    print()
    
    all_checks = []
    
    # 1. Verificar archivos esenciales
    print("📁 VERIFICANDO ARCHIVOS ESENCIALES...")
    print("-" * 60)
    all_checks.append(check_file_exists('build.sh', 'Script de construcción'))
    all_checks.append(check_file_exists('render.yaml', 'Configuración Render'))
    all_checks.append(check_file_exists('requirements.txt', 'Dependencias Python'))
    all_checks.append(check_file_exists('manage.py', 'Archivo manage.py'))
    all_checks.append(check_file_exists('EcoFactProject/settings.py', 'Configuración Django'))
    all_checks.append(check_file_exists('EcoFactProject/wsgi.py', 'Archivo WSGI'))
    print()
    
    # 2. Verificar requirements.txt
    print("📦 VERIFICANDO DEPENDENCIAS...")
    print("-" * 60)
    all_checks.append(check_requirements())
    print()
    
    # 3. Verificar settings.py
    print("⚙️  VERIFICANDO CONFIGURACIÓN DJANGO...")
    print("-" * 60)
    all_checks.append(check_settings())
    print()
    
    # 4. Verificar build.sh
    print("🔨 VERIFICANDO SCRIPT DE CONSTRUCCIÓN...")
    print("-" * 60)
    all_checks.append(check_build_script())
    print()
    
    # 5. Verificar .gitignore
    print("🚫 VERIFICANDO EXCLUSIONES GIT...")
    print("-" * 60)
    if check_file_exists('.gitignore', 'Archivo .gitignore'):
        with open('.gitignore', 'r') as f:
            content = f.read()
            if '.env' in content:
                print("✅ .env está en .gitignore (no se subirá a GitHub)")
            else:
                print("⚠️  .env NO está en .gitignore (¡PRECAUCIÓN!)")
    print()
    
    # Resumen final
    print("=" * 60)
    print("📊 RESUMEN")
    print("=" * 60)
    
    passed = sum(all_checks)
    total = len(all_checks)
    
    if passed == total:
        print(f"✅ TODAS LAS VERIFICACIONES PASARON ({passed}/{total})")
        print()
        print("🚀 ¡Tu proyecto está listo para desplegarse en Render!")
        print()
        print("Próximos pasos:")
        print("1. git add .")
        print("2. git commit -m 'Configuración para Render'")
        print("3. git push origin main")
        print("4. Ir a Render y conectar tu repositorio")
        print()
        print("📖 Lee DESPLIEGUE_RENDER.md para instrucciones detalladas")
    else:
        print(f"⚠️  ALGUNAS VERIFICACIONES FALLARON ({passed}/{total} pasaron)")
        print()
        print("Por favor, revisa los errores arriba y corrígelos antes de desplegar.")
        sys.exit(1)
    
    print("=" * 60)

if __name__ == "__main__":
    main()
