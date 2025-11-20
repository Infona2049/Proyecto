# EcoFact - Sistema de Facturación

Sistema de facturación con autenticación por roles desarrollado en Django.

## 🚀 Configuración Rápida para Nuevos Miembros (Recomendado)

### Opción A: Script Automático (Más Fácil)

**En Windows:**
```bash
git clone https://github.com/Infona2049/front-ecofact.git
cd front-ecofact
setup.bat
```


### Opción B: Configuración Manual

## 🚀 Instalación y Configuración para Nuevos Miembros del Equipo

### Requisitos previos
- Python 3.11 o superior
- Git

### 1. Clonar el repositorio
```bash
git clone https://github.com/Infona2049/front-ecofact.git
cd front-ecofact
```

### 2. Crear entorno virtual
```bash
python -m venv venv
```

### 3. Activar entorno virtual
**En Windows:**
```bash
venv\Scripts\activate
```

**En Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 5. Configurar variables de entorno
```bash
copy .env.example .env
```

**✅ CONFIGURACIÓN ACTUAL: Base de datos Neon (en la nube)**
El proyecto ya está configurado para usar Neon. El archivo `.env.example` 
contiene las credenciales correctas de la base de datos compartida.

### 6. Ejecutar migraciones (solo primera vez)
```bash
python manage.py migrate
```

### 7. Crear superusuario para panel admin (opcional)
```bash
python manage.py create_superuser
```
Esto te permitirá acceder a http://localhost:8001/admin/ para gestionar usuarios.

### 8. Ejecutar el servidor
```bash
python manage.py runserver 8001
```

### 9. ¡Listo! Acceder a la aplicación
- **Aplicación principal:** http://localhost:8001/
- **Panel de administración:** http://localhost:8001/admin/

## 🔗 Configuración para Equipos

### ✅ **Configuración Actual: Base de Datos en la Nube (Neon)**

**¡El proyecto ya está configurado para trabajo en equipo!**

- 🌐 **Base de datos compartida:** Todos acceden a la misma BD en Neon
- 🔄 **Datos sincronizados:** Cambios en tiempo real para todo el equipo  
- 🚀 **Sin configuración adicional:** Solo hacer `git pull` y usar

### 🔧 **Configuración para nuevos miembros:**

```bash
# 1. Clonar repositorio
git clone https://github.com/Infona2049/front-ecofact.git
cd front-ecofact

# 2. Crear entorno virtual  
python -m venv venv
venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Copiar configuración (ya tiene credenciales de Neon)
copy .env.example .env

# 5. ¡Listo! La BD ya está configurada
python manage.py runserver 8001
```

### 👥 **Usuarios disponibles para todos:**
- **Admin:** admin@ecofact.com / admin123
- **Vendedor:** vendedor@ecofact.com / vendedor123  
- **Cliente:** cliente@ecofact.com / cliente123

### 📊 **Ventajas de la configuración actual:**
- ✅ **Base de datos compartida en la nube**
- ✅ **Sin conflictos entre miembros del equipo**
- ✅ **Acceso desde cualquier ubicación**
- ✅ **Backup automático en Neon**
- ✅ **512MB gratuitos (más que suficiente)**

## 🔐 Usuarios de Prueba

| Rol | Email | Contraseña | URL de acceso |
|-----|-------|------------|---------------|
| **Superadmin** | superadmin@ecofact.com | superadmin123 | `/admin/` (Django Admin) |
| **Administrador** | admin@ecofact.com | admin123 | `/admin-dashboard/` |
| **Vendedor** | vendedor@ecofact.com | vendedor123 | `/vendedor-dashboard/` |
| **Cliente** | cliente@ecofact.com | cliente123 | `/cliente-dashboard/` |

> **Nota:** Los usuarios se crean automáticamente con los scripts de instalación.

## 🌐 URLs Principales

- **Página principal:** `http://127.0.0.1:8001/` (redirige al login)
- **Login:** `http://127.0.0.1:8001/login/`
- **Registro:** `http://127.0.0.1:8001/registro/`
- **Admin Panel:** `http://127.0.0.1:8001/admin/`

## 📱 Funcionalidades

### ✅ Implementadas
- [x] Sistema de autenticación por email
- [x] Registro de nuevos usuarios (solo clientes)
- [x] Login con redirección automática por rol
- [x] Dashboards específicos por rol
- [x] Control de acceso por decoradores
- [x] Gestión de archivos estáticos
- [x] Base de datos con SQLite

### 🔄 Sistema de Roles
- **Admin:** Acceso completo al sistema
- **Vendedor:** Gestión de productos y ventas
- **Cliente:** Visualización de productos y facturas

## 🛠️ Estructura del Proyecto

```
front-ecofact/
├── core/                   # App principal
│   ├── models.py          # Modelos de usuario y facturación
│   ├── views.py           # Vistas de login, registro, dashboards
│   ├── forms.py           # Formularios de registro
│   ├── templates/         # Templates HTML
│   └── static/            # CSS y JS
├── productos/             # App de productos
├── static/                # Archivos estáticos globales
├── EcoFactProject/        # Configuración del proyecto
├── manage.py
├── requirements.txt       # Dependencias
└── README.md             # Este archivo
```

## 🐛 Solución de Problemas

### Error de puerto ocupado
Si el puerto 8000 está ocupado, usa otro puerto:
```bash
python manage.py runserver 8001
```

### Error de migraciones
Si hay problemas con la base de datos:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Error de archivos estáticos
Si las imágenes no cargan, verifica que el servidor esté ejecutándose y que las rutas en los templates usen `{% static 'img/nombre-imagen.png' %}`.

## 📝 Notas de Desarrollo

- **Base de datos:** SQLite (para desarrollo)
- **Puerto por defecto:** 8001 (evita conflictos)
- **Archivos de media:** Las imágenes están en `static/img/`
- **Registro:** Solo permite crear usuarios con rol "Cliente"


## 📞 Contacto

Si tienes problemas con la instalación o ejecución, contacta al equipo de desarrollo.

---
**Desarrollado por:** Equipo EcoFact  
**Última actualización:** Septiembre 2025