# 🔧 Comandos Útiles Post-Despliegue en Render

## 📍 Cómo acceder al Shell de Render

1. Ve a https://dashboard.render.com/
2. Selecciona tu servicio web "ecofact-project"
3. En el menú izquierdo, haz clic en **"Shell"**
4. Espera a que cargue la terminal

---

## 👤 Gestión de Usuarios

### Crear un superusuario
```bash
python manage.py createsuperuser
```

### Crear usuarios de prueba (si tienes el comando personalizado)
```bash
python manage.py create_test_users
```

### Ver todos los usuarios
```bash
python manage.py shell
```
Luego en el shell de Django:
```python
from core.models import Usuario
usuarios = Usuario.objects.all()
for u in usuarios:
    print(f"{u.username} - {u.email} - Rol: {u.rol}")
```

### Desbloquear un usuario
```bash
python manage.py unlock_user nombre_usuario
```

### Verificar estado del login
```bash
python manage.py check_login_status
```

---

## 🗄️ Comandos de Base de Datos

### Ver estado de las migraciones
```bash
python manage.py showmigrations
```

### Ejecutar migraciones manualmente
```bash
python manage.py migrate
```

### Crear nuevas migraciones (si cambias modelos)
```bash
python manage.py makemigrations
python manage.py migrate
```

### Acceder al shell de la base de datos
```bash
python manage.py dbshell
```

### Ver todas las tablas
```bash
python manage.py shell
```
```python
from django.db import connection
tables = connection.introspection.table_names()
print(tables)
```

---

## 📊 Comandos de Datos

### Ver cantidad de productos
```bash
python manage.py shell
```
```python
from productos.models import Producto
print(f"Total productos: {Producto.objects.count()}")
```

### Ver cantidad de facturas
```bash
python manage.py shell
```
```python
from facturas.models import Factura
print(f"Total facturas: {Factura.objects.count()}")
```

### Limpiar facturas antiguas (ejemplo)
```python
from facturas.models import Factura
from django.utils import timezone
from datetime import timedelta

# Eliminar facturas de más de 30 días
fecha_limite = timezone.now() - timedelta(days=30)
facturas_antiguas = Factura.objects.filter(fecha_expedicion__lt=fecha_limite)
print(f"Se eliminarán {facturas_antiguas.count()} facturas")
# facturas_antiguas.delete()  # Descomenta para eliminar
```

---

## 📁 Archivos Estáticos

### Recolectar archivos estáticos manualmente
```bash
python manage.py collectstatic --no-input
```

### Ver dónde están los archivos estáticos
```bash
python manage.py shell
```
```python
from django.conf import settings
print(f"STATIC_ROOT: {settings.STATIC_ROOT}")
print(f"STATIC_URL: {settings.STATIC_URL}")
```

---

## 🔍 Diagnóstico y Debugging

### Ver configuración actual
```bash
python manage.py diffsettings
```

### Ver configuración de la base de datos
```bash
python manage.py shell
```
```python
from django.conf import settings
print(settings.DATABASES)
```

### Verificar configuración de email
```bash
python manage.py shell
```
```python
from django.conf import settings
print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
```

### Probar envío de email
```bash
python manage.py shell
```
```python
from django.core.mail import send_mail
send_mail(
    'Test desde Render',
    'Este es un email de prueba',
    'ecofactproyect@gmail.com',
    ['tu_email@example.com'],
    fail_silently=False,
)
print("Email enviado!")
```

---

## 🔄 Actualizar la Aplicación

### Después de hacer cambios en el código local:

```bash
# En tu máquina local:
git add .
git commit -m "Descripción de los cambios"
git push origin main

# Render detectará el push y automáticamente:
# 1. Descargará el nuevo código
# 2. Ejecutará build.sh
# 3. Reiniciará la aplicación
```

### Forzar un redespliegue manual:
1. Ve a tu servicio en Render
2. Click en **"Manual Deploy"**
3. Selecciona la rama (main)
4. Click en **"Deploy"**

---

## 📋 Backup y Restauración

### Crear un backup de la base de datos
```bash
# Desde el shell de Render
python manage.py dumpdata > backup.json
```

### Descargar el backup (desde tu máquina local)
Render no permite descargas directas, pero puedes:
1. Subir el backup a un servicio como GitHub Gist
2. O usar `python manage.py dumpdata --output backup.json` y luego descargarlo

### Restaurar desde un backup
```bash
python manage.py loaddata backup.json
```

---

## 🔐 Seguridad

### Cambiar SECRET_KEY
1. Ve a tu servicio en Render
2. Click en **"Environment"**
3. Busca `SECRET_KEY`
4. Click en **"Generate"** para una nueva
5. Guarda los cambios (se reiniciará automáticamente)

### Ver variables de entorno
```bash
python manage.py shell
```
```python
import os
from django.conf import settings

print(f"DEBUG: {settings.DEBUG}")
print(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
print(f"SECRET_KEY: {settings.SECRET_KEY[:10]}...")  # Solo primeros 10 caracteres
```

---

## 📈 Monitoreo

### Ver logs en tiempo real
1. Ve a tu servicio en Render
2. Click en **"Logs"**
3. Los logs se actualizan automáticamente

### Ver logs desde el shell
```bash
# Los logs se muestran automáticamente en la consola de Render
# No hay un comando específico para verlos desde el shell
```

### Filtrar logs por error
En la página de Logs de Render, busca:
- `ERROR` - para errores
- `WARNING` - para advertencias
- `Exception` - para excepciones

---

## 🧪 Testing

### Ejecutar tests
```bash
python manage.py test
```

### Ejecutar tests de una app específica
```bash
python manage.py test core
python manage.py test productos
python manage.py test facturas
```

### Ejecutar un test específico
```bash
python manage.py test core.tests.TestLogin
```

---

## 🗑️ Limpieza

### Limpiar sesiones expiradas
```bash
python manage.py clearsessions
```

### Eliminar archivos de migración no aplicados
```bash
# ¡CUIDADO! Solo si sabes lo que haces
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete
```

---

## 💾 Base de Datos PostgreSQL

### Conectarse directamente a PostgreSQL

Desde el dashboard de Render:
1. Ve a **"Databases"**
2. Selecciona **"ecofact-db"**
3. Copia las credenciales
4. Usa un cliente PostgreSQL como:
   - pgAdmin
   - DBeaver
   - TablePlus

### Comando psql (si está disponible)
```bash
psql $DATABASE_URL
```

Comandos útiles en psql:
```sql
\dt                    -- Listar todas las tablas
\d core_usuario        -- Describir tabla de usuarios
SELECT COUNT(*) FROM core_usuario;
SELECT COUNT(*) FROM facturas_factura;
\q                     -- Salir
```

---

## 🔄 Reiniciar Servicios

### Reiniciar el servicio web
1. Ve a tu servicio en Render
2. En la esquina superior derecha
3. Click en **"⋯"** (tres puntos)
4. Click en **"Restart"**

### Reiniciar la base de datos
⚠️ **CUIDADO**: Esto puede causar tiempo de inactividad
1. Ve a "Databases"
2. Selecciona tu base de datos
3. Click en "⋯" → "Restart"

---

## 📞 Obtener Información del Sistema

### Ver versión de Python
```bash
python --version
```

### Ver versión de Django
```bash
python manage.py version
```

### Ver todas las dependencias instaladas
```bash
pip list
```

### Ver información del sistema
```bash
python manage.py shell
```
```python
import sys
import django
import platform

print(f"Python: {sys.version}")
print(f"Django: {django.get_version()}")
print(f"Platform: {platform.platform()}")
```

---

## 🎯 Scripts Personalizados

Si creaste comandos personalizados en `core/management/commands/`:

```bash
# Listar todos los comandos disponibles
python manage.py help

# Ejecutar tu comando personalizado
python manage.py tu_comando
```

---

## 🚨 Solución de Problemas Comunes

### "Application failed to start"
```bash
# Ver los logs completos
# Desde el dashboard → Logs

# Verificar que build.sh se ejecutó correctamente
cat build.sh
```

### "Static files not found"
```bash
# Recolectar manualmente
python manage.py collectstatic --no-input

# Verificar configuración
python manage.py shell
```
```python
from django.conf import settings
print(settings.STATIC_ROOT)
print(settings.STATIC_URL)
```

### "Database connection error"
```bash
# Verificar DATABASE_URL
python manage.py shell
```
```python
import os
print(os.environ.get('DATABASE_URL')[:50])  # Primeros 50 caracteres
```

---

## 📝 Notas Importantes

1. **Shell Access**: El shell de Render es temporal, los archivos que crees no persisten
2. **Timezone**: Por defecto está en UTC, considera esto para fechas
3. **Límites**: El plan gratuito tiene límites de CPU y memoria
4. **Dormido**: La app se duerme después de 15 minutos de inactividad

---

¡Guarda este archivo para referencia rápida! 📌
