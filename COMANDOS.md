# COMANDOS ÚTILES - ECOFACT

## Configuración inicial (solo una vez)
```bash
# Configuración automática
setup.bat  # Windows
./setup.sh # Linux/Mac

# O manual:
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
```

## Comandos diarios
```bash
# Activar entorno virtual
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Iniciar servidor
python manage.py runserver 8001

# Actualizar desde Git
git pull origin master
pip install -r requirements.txt  # Si hay nuevas dependencias
python manage.py migrate  # Si hay nuevas migraciones
```

## Gestión de usuarios

### Panel de administración (Recomendado)
```
1. Ve a http://localhost:8001/admin/
2. Usuario: superadmin@ecofact.com
3. Pass: superadmin123
4. Click en "Users" → "Add" para crear nuevos admin/vendedor
```

### Por comando (Alternativo)
```bash
# Crear superusuario
python manage.py create_superuser

# Crear usuario específico
python manage.py create_user --email nuevo@ecofact.com --password 123456 --nombre Juan --apellido Perez --documento 12345678 --rol admin
```

## Usuarios predeterminados
- **Superadmin:** superadmin@ecofact.com / superadmin123 (Django Admin)
- **Admin:** admin@ecofact.com / admin123
- **Vendedor:** vendedor@ecofact.com / vendedor123
- **Cliente:** cliente@ecofact.com / cliente123

> **Nota:** Estos usuarios se crean automáticamente al ejecutar los scripts de instalación.

## URLs importantes
- **Aplicación:** http://localhost:8001/
- **Login:** http://localhost:8001/login/
- **Registro:** http://localhost:8001/registro/
- **Admin:** http://localhost:8001/admin/

## Base de datos
- **Tipo:** PostgreSQL en Neon (nube)
- **Compartida:** Todos los miembros acceden a la misma BD
- **Configuración:** Automática en .env.example