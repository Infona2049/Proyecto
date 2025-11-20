# 🚀 Guía Completa de Despliegue en Render

## 📋 Archivos Preparados

✅ **build.sh** - Script de construcción automática
✅ **render.yaml** - Configuración de servicios (Web + Base de datos)
✅ **requirements.txt** - Dependencias actualizadas con gunicorn, whitenoise y dj-database-url
✅ **settings.py** - Configurado para producción con Render

---

## 🔧 Pasos para Desplegar

### 1️⃣ Preparar el Repositorio

```bash
# Asegúrate de estar en la carpeta del proyecto
cd c:\Users\juand\Desktop\Proyecto

# Agregar todos los cambios
git add .

# Hacer commit
git commit -m "Configuración completa para despliegue en Render"

# Subir a GitHub
git push origin main
```

---

### 2️⃣ Crear Cuenta en Render

1. Ve a [render.com](https://render.com/)
2. Haz clic en **"Get Started for Free"**
3. Regístrate con tu cuenta de GitHub

---

### 3️⃣ Conectar el Repositorio

1. En el dashboard de Render, haz clic en **"New +"**
2. Selecciona **"Blueprint"** (esto detectará automáticamente el archivo `render.yaml`)
3. Busca y selecciona tu repositorio **"Proyecto"**
4. Haz clic en **"Connect"**

---

### 4️⃣ Configurar Variables de Entorno

Render detectará automáticamente la mayoría de las variables del `render.yaml`, pero necesitas configurar las de email:

#### En la configuración del servicio web:

1. Ve a **Environment** en el panel izquierdo
2. Agrega las siguientes variables que no se generan automáticamente:

```
EMAIL_HOST_USER = ecofactproyect@gmail.com
EMAIL_HOST_PASSWORD = ynoffupvodsyozjl
DEFAULT_FROM_EMAIL = ecofactproyect@gmail.com
```

**Nota:** Render generará automáticamente:
- `SECRET_KEY` (nueva clave segura)
- `DATABASE_URL` (conexión a la base de datos PostgreSQL)

---

### 5️⃣ Desplegar

1. Haz clic en **"Apply"** para crear los servicios
2. Render comenzará a:
   - Crear la base de datos PostgreSQL
   - Construir el servicio web
   - Ejecutar el script `build.sh` que:
     - Instala dependencias
     - Recolecta archivos estáticos
     - Ejecuta migraciones
   - Iniciar la aplicación con Gunicorn

---

### 6️⃣ Verificar el Despliegue

1. Espera a que el despliegue termine (puede tomar 5-10 minutos)
2. Verás un mensaje **"Deploy succeeded"** en verde
3. Haz clic en el URL que Render te proporciona (algo como `https://ecofact-project.onrender.com`)
4. ¡Tu aplicación estará en vivo! 🎉

---

## 🔍 Monitoreo y Logs

### Ver logs en tiempo real:
1. Ve a tu servicio en el dashboard de Render
2. Haz clic en **"Logs"** en el panel izquierdo
3. Verás todos los logs de la aplicación

### Verificar la base de datos:
1. Ve a **"Databases"** en el dashboard
2. Haz clic en **"ecofact-db"**
3. Puedes conectarte usando las credenciales proporcionadas

---

## 🛠️ Comandos Útiles Post-Despliegue

### Crear un superusuario en Render:

1. Ve a tu servicio web en Render
2. Haz clic en **"Shell"** en el panel izquierdo
3. Ejecuta:

```bash
python manage.py createsuperuser
```

### Ejecutar migraciones manualmente:

```bash
python manage.py migrate
```

### Recolectar archivos estáticos manualmente:

```bash
python manage.py collectstatic --no-input
```

---

## 📊 Arquitectura del Despliegue

```
┌─────────────────────────────────────────┐
│         Render Blueprint                │
├─────────────────────────────────────────┤
│                                         │
│  ┌───────────────────────────────────┐ │
│  │   Web Service (Python)            │ │
│  │   - Django 5.2.4                  │ │
│  │   - Gunicorn WSGI Server          │ │
│  │   - WhiteNoise (Static Files)     │ │
│  │   - Free Plan                     │ │
│  └───────────────┬───────────────────┘ │
│                  │                      │
│                  │ DATABASE_URL         │
│                  │                      │
│  ┌───────────────▼───────────────────┐ │
│  │   PostgreSQL Database             │ │
│  │   - Database: ecofact             │ │
│  │   - User: ecofact                 │ │
│  │   - Free Plan (256 MB)            │ │
│  └───────────────────────────────────┘ │
│                                         │
└─────────────────────────────────────────┘
```

---

## ⚙️ Configuraciones Aplicadas

### 1. **settings.py**
- ✅ `ALLOWED_HOSTS` configurado dinámicamente
- ✅ `WhiteNoise` para servir archivos estáticos
- ✅ `dj-database-url` para conexión automática a PostgreSQL
- ✅ Configuración de `STATIC_ROOT` y `STATICFILES_STORAGE`

### 2. **build.sh**
- ✅ Instalación de dependencias
- ✅ Recolección de archivos estáticos
- ✅ Ejecución de migraciones

### 3. **render.yaml**
- ✅ Servicio web Python con Gunicorn
- ✅ Base de datos PostgreSQL
- ✅ Variables de entorno configuradas
- ✅ Plan gratuito para ambos servicios

---

## 🔄 Actualizaciones Futuras

Cada vez que hagas cambios en tu código:

```bash
# 1. Hacer commit de los cambios
git add .
git commit -m "Descripción de los cambios"

# 2. Subir a GitHub
git push origin main

# 3. Render detectará el push y automáticamente:
#    - Descargará el nuevo código
#    - Ejecutará build.sh
#    - Reiniciará la aplicación
```

---

## 🆘 Solución de Problemas

### Error: "Application failed to start"
- Verifica los logs en Render
- Asegúrate de que `build.sh` tiene permisos de ejecución
- Verifica que todas las variables de entorno estén configuradas

### Error: "Static files not found"
- Ejecuta manualmente: `python manage.py collectstatic --no-input`
- Verifica que `STATIC_ROOT` esté configurado correctamente

### Error de conexión a la base de datos
- Verifica que `DATABASE_URL` esté configurada en las variables de entorno
- Asegúrate de que el servicio de base de datos esté en estado "Available"

---

## 📧 Configuración de Email

La aplicación usa Gmail para enviar correos. Las credenciales ya están configuradas:
- **Host:** smtp.gmail.com
- **Usuario:** ecofactproyect@gmail.com
- **Password:** (App Password configurado)
- **Puerto:** 587
- **TLS:** Habilitado

---

## 🎯 Checklist Final

- [ ] Código subido a GitHub
- [ ] Blueprint aplicado en Render
- [ ] Variables de entorno configuradas
- [ ] Despliegue exitoso (sin errores)
- [ ] URL de la aplicación accesible
- [ ] Base de datos creada y conectada
- [ ] Archivos estáticos cargados correctamente
- [ ] Sistema de login funcional
- [ ] Correos electrónicos funcionando

---

## 🌐 URLs Importantes

- **Dashboard Render:** https://dashboard.render.com/
- **Documentación Render:** https://render.com/docs
- **Tu aplicación:** `https://[tu-servicio].onrender.com`

---

## 💡 Notas Importantes

1. **Plan Gratuito:** El plan gratuito de Render tiene algunas limitaciones:
   - La aplicación se "duerme" después de 15 minutos de inactividad
   - El primer acceso después de dormir puede tomar 30-60 segundos
   - 750 horas gratis al mes
   - Base de datos de 256 MB

2. **HTTPS:** Render proporciona HTTPS gratuito automáticamente

3. **Dominio Personalizado:** Puedes configurar tu propio dominio en la configuración del servicio

---

¡Listo! Tu proyecto EcoFact está completamente preparado para desplegarse en Render. 🚀
