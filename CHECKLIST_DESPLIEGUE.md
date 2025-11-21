# ✅ CHECKLIST DE DESPLIEGUE RENDER

## 📦 ANTES DE DESPLEGAR

### Preparación Local
- [ ] Todos los cambios guardados y funcionando localmente
- [ ] Base de datos local actualizada con migraciones
- [ ] Archivos estáticos cargando correctamente en local
- [ ] Sistema de login funcionando
- [ ] Correos enviándose correctamente

### Archivos del Proyecto
- [ ] `build.sh` existe
- [ ] `render.yaml` existe y está configurado
- [ ] `requirements.txt` tiene gunicorn, whitenoise, dj-database-url
- [ ] `settings.py` configurado para producción
- [ ] `.gitignore` incluye `.env` y archivos sensibles
- [ ] `.env` NO está en el repositorio (solo .env.example)

---

## 🚀 DURANTE EL DESPLIEGUE

### Git y GitHub
- [ ] `git status` - Verificar archivos modificados
- [ ] `git add .` - Agregar todos los cambios
- [ ] `git commit -m "Preparado para Render"` - Hacer commit
- [ ] `git push origin main` - Subir a GitHub
- [ ] Verificar en GitHub que los archivos se subieron

### Render - Configuración Inicial
- [ ] Cuenta creada en https://render.com/
- [ ] Conectado con GitHub
- [ ] Click en "New +" → "Blueprint"
- [ ] Repositorio "Proyecto" seleccionado y conectado
- [ ] Render detectó `render.yaml` automáticamente

### Render - Variables de Entorno
- [ ] `EMAIL_HOST_USER` configurado
- [ ] `EMAIL_HOST_PASSWORD` configurado
- [ ] `DEFAULT_FROM_EMAIL` configurado
- [ ] Verificar que `SECRET_KEY` se generó automáticamente
- [ ] Verificar que `DATABASE_URL` está conectado a la BD

### Render - Despliegue
- [ ] Click en "Apply" para iniciar despliegue
- [ ] Esperar a que se cree la base de datos PostgreSQL
- [ ] Esperar a que se construya el servicio web
- [ ] Ver los logs en tiempo real (opcional)

---

## ✅ DESPUÉS DEL DESPLIEGUE

### Verificación Básica
- [ ] Despliegue completado sin errores (verde ✓)
- [ ] URL de la aplicación generada
- [ ] Abrir la URL en el navegador
- [ ] La página carga sin errores 500/404
- [ ] Los estilos CSS se ven correctamente
- [ ] Las imágenes cargan correctamente

### Verificación de Funcionalidades

#### Sistema de Login
- [ ] Página de login carga (`/login/`)
- [ ] Página de registro carga (`/registro/`)
- [ ] Intentar hacer login (crear usuario primero si es necesario)
- [ ] Login exitoso redirige correctamente
- [ ] Sistema de roles funciona (admin, vendedor, cliente)

#### Base de Datos
- [ ] Acceder al Shell de Render
- [ ] Ejecutar `python manage.py showmigrations`
- [ ] Todas las migraciones aplicadas (marcadas con [X])
- [ ] Crear un superusuario: `python manage.py createsuperuser`
- [ ] Login con superusuario funciona

#### Panel de Administración
- [ ] Acceder a `/admin/`
- [ ] Login con superusuario
- [ ] Ver usuarios en el admin
- [ ] Ver productos en el admin
- [ ] Ver facturas en el admin

#### Productos
- [ ] Página de inventario carga
- [ ] Página de registro de productos carga
- [ ] Crear un producto de prueba
- [ ] Producto aparece en el inventario
- [ ] Buscar producto funciona

#### Facturas
- [ ] Página de creación de facturas carga
- [ ] Crear una factura de prueba
- [ ] Factura se guarda correctamente
- [ ] Ver historial de facturas
- [ ] Imprimir factura funciona
- [ ] QR code se genera correctamente

#### Sistema de Correos
- [ ] Recuperación de contraseña funciona
- [ ] Correo de bienvenida se envía (si aplica)
- [ ] Verificar bandeja de entrada del correo de prueba

### Archivos Estáticos
- [ ] CSS de login carga
- [ ] CSS de registro carga
- [ ] CSS de inventario carga
- [ ] CSS de facturas carga
- [ ] JavaScript funciona correctamente
- [ ] Imágenes del proyecto cargan

---

## 🔧 CONFIGURACIÓN POST-DESPLIEGUE

### Usuarios Iniciales
- [ ] Crear superadmin: `python manage.py createsuperuser`
- [ ] Crear usuarios de prueba (opcional): `python manage.py create_test_users`
- [ ] Verificar que los usuarios fueron creados

### Datos Iniciales (si aplica)
- [ ] Cargar productos iniciales
- [ ] Cargar categorías
- [ ] Configurar permisos personalizados

### Monitoreo
- [ ] Activar notificaciones de errores en Render
- [ ] Revisar logs periódicamente
- [ ] Configurar alertas (opcional)

---

## 📊 PRUEBAS COMPLETAS

### Prueba del Flujo Completo Cliente
- [ ] Registrarse como nuevo cliente
- [ ] Activar cuenta (si hay activación por email)
- [ ] Hacer login
- [ ] Ver productos disponibles
- [ ] Navegar por el sitio

### Prueba del Flujo Completo Vendedor
- [ ] Login como vendedor
- [ ] Acceder a inventario
- [ ] Agregar un producto nuevo
- [ ] Editar un producto existente
- [ ] Crear una factura
- [ ] Ver historial de facturas
- [ ] Imprimir una factura

### Prueba del Flujo Completo Admin
- [ ] Login como admin
- [ ] Acceder al panel de administración
- [ ] Ver todos los usuarios
- [ ] Ver todas las facturas
- [ ] Ver todos los productos
- [ ] Gestionar permisos
- [ ] Ver estadísticas (si aplica)

---

## 🐛 DEPURACIÓN (Si algo falla)

### Revisar Logs
- [ ] Abrir página de Logs en Render
- [ ] Buscar mensajes de ERROR
- [ ] Buscar mensajes de WARNING
- [ ] Buscar excepciones de Python
- [ ] Copiar errores relevantes

### Verificar Build
- [ ] Ver que `build.sh` se ejecutó completo
- [ ] Ver que `pip install` completó
- [ ] Ver que `collectstatic` completó
- [ ] Ver que `migrate` completó
- [ ] Ver que Gunicorn inició correctamente

### Verificar Variables de Entorno
- [ ] Ir a Environment en Render
- [ ] Verificar que todas las variables existen
- [ ] Verificar que no hay typos
- [ ] Verificar valores secretos (sin mostrar)

### Problemas Comunes
- [ ] Si 500: Revisar logs del servidor
- [ ] Si 404: Verificar configuración de URLs
- [ ] Si CSS no carga: Verificar STATIC_ROOT y collectstatic
- [ ] Si BD falla: Verificar DATABASE_URL
- [ ] Si email falla: Verificar credenciales SMTP

---

## 📱 COMPARTIR CON EL EQUIPO

### Información a Compartir
- [ ] URL de la aplicación: `https://_____.onrender.com`
- [ ] Usuarios de prueba creados
- [ ] Credenciales de prueba (si aplica)
- [ ] Link al repositorio de GitHub
- [ ] Documentación del proyecto

### Accesos
- [ ] Invitar miembros del equipo a GitHub
- [ ] Compartir credenciales de Render (si es necesario)
- [ ] Compartir credenciales de email (admin)
- [ ] Documentar el proceso para el equipo

---

## 🎉 DESPLIEGUE EXITOSO

### Confirmar Todo Funciona
- [ ] ✅ Aplicación accesible vía HTTPS
- [ ] ✅ Login funcional
- [ ] ✅ Base de datos operativa
- [ ] ✅ Archivos estáticos cargando
- [ ] ✅ Sistema de emails funcionando
- [ ] ✅ CRUD de productos funcional
- [ ] ✅ Sistema de facturas funcional
- [ ] ✅ Sin errores en los logs

### Celebrar 🎊
- [ ] Tomar captura de pantalla de la app en vivo
- [ ] Actualizar README con el link de la app
- [ ] Compartir con el equipo
- [ ] ¡Celebrar el éxito! 🚀

---

## 📌 LINKS IMPORTANTES

- **Dashboard Render**: https://dashboard.render.com/
- **Tu App**: `https://_____.onrender.com` (llenar después)
- **GitHub Repo**: https://github.com/Infona2049/Proyecto
- **Guía Completa**: Ver `DESPLIEGUE_RENDER.md`
- **Comandos Útiles**: Ver `COMANDOS_RENDER.md`

---

## 🔄 MANTENIMIENTO CONTINUO

### Cada Actualización
- [ ] Probar cambios localmente
- [ ] Hacer commit con mensaje descriptivo
- [ ] Push a GitHub (Render se actualiza automáticamente)
- [ ] Verificar que el redespliegue fue exitoso
- [ ] Probar la funcionalidad actualizada en producción

### Mensualmente
- [ ] Revisar logs por errores
- [ ] Verificar espacio en base de datos
- [ ] Limpiar sesiones expiradas
- [ ] Hacer backup de datos importantes
- [ ] Actualizar dependencias si es necesario

---

**Fecha de Despliegue**: ________________

**Desplegado por**: ________________

**Notas adicionales**:
_________________________________________
_________________________________________
_________________________________________

---

✅ **TODO LISTO PARA DESPLEGAR EN RENDER**
