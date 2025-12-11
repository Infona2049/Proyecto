# EcoFact - Sistema de Facturación

Sistema de facturación con autenticación por roles desarrollado en Django.

 Configuración Rápida para Nuevos Miembros (Recomendado)




##  Instalación y Configuración para Nuevos Miembros del Equipo

### Requisitos previos
- Python 3.11 o superior
- Dependencias
- Django 5.2.4

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

### 4. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 5. Configurar variables de entorno
```bash
copy .env.example .env
```

** CONFIGURACIÓN ACTUAL: Base de datos Neon (La cual se encuentra en la nube)**
El proyecto  está configurado para usar Neon. El archivo `.env.example` 
contiene las credenciales correctas de la base de datos compartida.

### 6. Ejecutar migraciones la primera vez o cada que se hagan cambios en la base de datos
```bash
python manage.py migrate
```

### 7. Crear superusuario para panel de Administracion
```bash
python manage.py create_superuser
```


### 8. Ejecutar el servidor
```bash
python manage.py runserver 8000
```

### 9.  Acceder a la aplicación
- **Aplicación principal:** http://localhost:8000/
- **Panel de administración:** http://localhost:8000/admin/


###  **Configuración Actual: Base de Datos en la Nube (Neon)**

**¡El proyecto ya está configurado para trabajo en equipo!**

-  **Base de datos compartida:** Todos acceden a la misma BD en Neon
-  **Datos sincronizados:** Cambios en tiempo real para todo el equipo  
-  **Sin configuración adicional:** Solo hacer `git pull` y usar

### 🔧 **Configuración para nuevos miembros:**

```bash
# 1. Clonar repositorio
git clone https://https://github.com/Infona2049/Proyecto


# 2. Crear entorno virtual  
python -m venv venv
venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Copiar configuración (ya tiene credenciales de Neon)
copy .env.example .env

# 5. ¡Listo! La BD ya está configurada
python manage.py runserver 8000
```

###  **Usuarios disponibles pre creados:**
- **Admin:** admin@ecofact.com / admin123
- **Vendedor:** vendedor@ecofact.com / vendedor123  
- **Cliente:** cliente@ecofact.com / cliente123

###  **Ventajas de la configuración actual:**
-  **Base de datos compartida en la nube**
-  **Sin conflictos entre miembros del equipo**
-  **Acceso desde cualquier ubicación**
-  **Backup automático en Neon**
- 

##  Usuarios de Prueba

| Rol | Email | Contraseña | URL de acceso |
|-----|-------|------------|---------------|
| **Administrador** | admin@ecofact.com | admin123 | `/admin-dashboard/` |
| **Vendedor** | vendedor@ecofact.com | vendedor123 | `/vendedor-dashboard/` |
| **Cliente** | cliente@ecofact.com | cliente123 | `/cliente-dashboard/` |


##  URLs Principales

- **Página principal:** `http://127.0.0.1:8001/` (redirige al login)
- **Login:** `http://127.0.0.1:8001/login/`
- **Registro:** `http://127.0.0.1:8001/registro/`
- **Admin Panel:** `http://127.0.0.1:8001/admin/`



###  Sistema de Roles
- **Admin:** Acceso completo al sistema
- **Vendedor:** Gestión de productos y ventas
- **Cliente:** Visualización de productos y facturas




##  Arquitectura de Proyecto

```
Proyecto/
├── core/                           # Módulo de autenticación y usuarios
│   ├── models.py                  # Modelos: Usuario, CodigoRecuperacion, Empresa
│   ├── views.py                   # Vistas: login, registro, perfil, recuperación
│   ├── forms.py                   # Formularios: RegistroUsuarioForm, PerfilForm
│   ├── urls.py                    # Rutas de core
│   ├── middleware.py              # Middleware personalizado
│   ├── static/
│   │   └── core/
│   │       ├── css/               # Estilos CSS
│   │       └── js/                # Scripts JavaScript
│   └── templates/
│       └── core/
│           ├── login.html
│           ├── registro.html
│           ├── olvido_contraseña.html
│           ├── validacion_correo.html
│           ├── actualizar_perfil.html
│           └── emails/            # Plantillas de email
│               ├── recuperacion_contrasena.html
│               └── validacion_correo.html
│
├── productos/                      # Módulo de gestión de productos
│   ├── models.py                  # Modelos: Producto, Inventario, HistorialInventario
│   ├── views.py                   # Vistas CRUD de productos e inventario
│   ├── forms.py                   # Formularios de productos
│   ├── signals.py                 # Señales para historial automático
│   ├── urls.py                    # Rutas de productos
│   ├── static/
│   │   └── productos/
│   │       ├── css/               # Estilos
│   │       └── js/                # Scripts
│   └── templates/
│       └── productos/
│           ├── inventario.html
│           ├── registro_producto.html
│           └── historial_inventario.html
│
├── facturas/                       # Módulo de gestión de facturas
│   ├── models.py                  # Modelos: Factura, DetalleFactura, HistorialFactura
│   ├── views.py                   # Vistas CRUD de facturas
│   ├── urls.py                    # Rutas de facturas
│   ├── services.py                # Lógica de negocio de facturas
│   ├── static/
│   │   └── facturas/
│   │       ├── css/               # Estilos
│   │       ├── js/                # Scripts
│   │       └── img/               # Imágenes
│   └── templates/
│       └── facturas/
│           ├── crear_factura.html
│           ├── historial_factura.html
│           ├── factura_print.html
│           └── factura_exitosa.html
│
├── EcoFactProject/                # Configuración de Django
│   ├── settings.py                # Configuración principal
│   ├── urls.py                    # Rutas globales
│   ├── wsgi.py                    # WSGI para producción
│   └── asgi.py                    # ASGI para Websockets
│
├── static/                        # Archivos estáticos globales
│   └── img/                       # Imágenes compartidas (logos, iconos)
│
├── media/                         # Archivos subidos por usuarios
│   └── productos/                 # Imágenes de productos
│
├── manage.py                      # Script de gestión de Django
├── requirements.txt               # Dependencias del proyecto
├── db.sqlite3                     # Base de datos (desarrollo)
└── README.md                      # Información del proyecto
```




##  Solución de Problemas

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

##  Notas de Desarrollo

- **Base de datos:** SQLite (para desarrollo Integrada) y Neon en la nube
- **Puerto por defecto:** 8001 (evita conflictos)
- **Archivos de media:** Las imágenes están en `static/img/`
- **Registro:** Solo permite crear usuarios con rol "Cliente"


##  Contacto

Si tienes problemas con la instalación o ejecución, contacta al equipo de desarrollo.

---
**Desarrollado por:** Equipo de Desarrollo EcoFact  
**Última actualización:  **Diciembre
