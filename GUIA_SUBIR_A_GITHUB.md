# 🚀 Guía: Subir Cambios a GitHub y Configuración para el Equipo

## 📝 Resumen de Cambios Realizados

### Archivos Modificados
1. **`.env.example`** - Limpiado de credenciales reales
2. **`EcoFactProject/settings.py`** - (Restaurado al original)

### Archivos Nuevos Creados
1. **`CREDENTIALS.md`** - Credenciales reales del proyecto (⚠️ NO SUBIR A GITHUB)
2. **`SETUP_GUIDE.md`** - Guía de configuración para nuevos miembros
3. **`DOCUMENTACION_AUTENTICACION.md`** - Documentación técnica del sistema
4. **`GUIA_COMPLETA_RECUPERACION_PASSWORD.md`** - Guía detallada de recuperación

### Archivos Creados Localmente
- **`.env`** - Tu configuración local (⚠️ NO SUBIR - ya está en .gitignore)

---

## 🔒 PASO 1: Verificar que NO subirás archivos sensibles

### Verificar .gitignore

Ejecuta:
```bash
cat .gitignore
```

**Debe incluir:**
```
.env
.env.local
*.sqlite3
__pycache__/
staticfiles/
```

✅ **Tu `.gitignore` ya tiene `.env`**, así que está protegido.

---

## ⚠️ PASO 2: IMPORTANTE - NO subir CREDENTIALS.md

**CREDENTIALS.md contiene contraseñas reales.** Tienes dos opciones:

### Opción A: Agregarlo al .gitignore (Recomendado)

```bash
echo "CREDENTIALS.md" >> .gitignore
```

### Opción B: Eliminarlo del repositorio (si quieres compartirlo por otro medio)

```bash
git rm --cached CREDENTIALS.md
```

**Recomendación:** Usa Opción A y comparte `CREDENTIALS.md` por Discord/WhatsApp.

---

## 📤 PASO 3: Subir Cambios a GitHub

### 3.1 Ver qué archivos se subirán

```bash
git status
```

### 3.2 Agregar archivos al staging

```bash
# Agregar archivos específicos (recomendado)
git add .env.example
git add SETUP_GUIDE.md
git add DOCUMENTACION_AUTENTICACION.md
git add GUIA_COMPLETA_RECUPERACION_PASSWORD.md

# O agregar todo (excepto lo que está en .gitignore)
git add .
```

### 3.3 Verificar qué se va a subir

```bash
git status
```

**Deberías ver:**
```
Changes to be committed:
  modified:   .env.example
  new file:   SETUP_GUIDE.md
  new file:   DOCUMENTACION_AUTENTICACION.md
  new file:   GUIA_COMPLETA_RECUPERACION_PASSWORD.md
```

**NO deberías ver:**
- ❌ `.env`
- ❌ `CREDENTIALS.md` (si lo agregaste al .gitignore)

### 3.4 Hacer commit

```bash
git commit -m "docs: Mejorar seguridad y documentación del proyecto

- Limpiar .env.example de credenciales reales
- Agregar SETUP_GUIDE.md para nuevos miembros
- Agregar documentación técnica de autenticación
- Agregar guía completa de recuperación de contraseña
- Mejorar instrucciones de configuración"
```

### 3.5 Subir a GitHub

```bash
git push origin main
```

---

## 👥 PASO 4: Instrucciones para tus Compañeros

### Crea un mensaje para tu equipo:

```
🚀 ACTUALIZACIÓN DEL PROYECTO - ACCIÓN REQUERIDA

He actualizado el proyecto con mejoras de seguridad y documentación.

📋 PASOS PARA ACTUALIZAR TU ENTORNO LOCAL:

1. Actualizar código:
   git pull origin main

2. Crear/Actualizar archivo .env:
   copy .env.example .env

3. IMPORTANTE: Solicítame el archivo CREDENTIALS.md por Discord/WhatsApp
   (Contiene las credenciales reales de BD y email)

4. Copiar las credenciales del CREDENTIALS.md a tu archivo .env

5. Verificar que funciona:
   python manage.py runserver 8001

📚 NUEVA DOCUMENTACIÓN DISPONIBLE:
- SETUP_GUIDE.md - Guía de configuración completa
- DOCUMENTACION_AUTENTICACION.md - Cómo funciona el sistema de auth
- GUIA_COMPLETA_RECUPERACION_PASSWORD.md - Sistema de recuperación

❓ Si tienes problemas, revisa SETUP_GUIDE.md o pregúntame.
```

---

## 📧 PASO 5: Compartir CREDENTIALS.md de forma segura

### Opción A: Discord/WhatsApp (Recomendado)

1. Enviar el archivo `CREDENTIALS.md` por mensaje privado
2. Cada compañero lo guarda en su carpeta del proyecto
3. **NO lo suben a GitHub**

### Opción B: Google Drive (Carpeta privada)

1. Subir `CREDENTIALS.md` a carpeta privada de Google Drive
2. Compartir solo con el equipo
3. Cada uno lo descarga

### Opción C: Crear archivo .env directamente

Enviar por Discord/WhatsApp el contenido completo del `.env`:

```bash
USE_POSTGRESQL=True
DB_NAME=neondb
DB_USER=neondb_owner
DB_PASSWORD=npg_lXCDaqE7I5wh
DB_HOST=ep-divine-base-abk7yom6-pooler.eu-west-2.aws.neon.tech
DB_PORT=5432

SECRET_KEY=bgmcb%-*eu*np3_+jxb81d4!k_v@ws6qo3au(egm73i65f1ov_
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=ecofactproyect@gmail.com
EMAIL_HOST_PASSWORD=ynoffupvodsyozjl
EMAIL_PORT=587
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=ecofactproyect@gmail.com
```

---

## ✅ PASO 6: Verificación del Equipo

Cada compañero debe verificar:

```bash
# 1. Actualizar código
git pull origin main

# 2. Verificar que tienen .env
dir .env  # Windows
ls .env   # Linux/Mac

# 3. Verificar que Django inicia sin errores
python manage.py check

# 4. Iniciar servidor
python manage.py runserver 8001

# 5. Probar login
# Ir a http://localhost:8001/login/
# Usar: admin@ecofact.com / admin123
```

---

## 🔐 PASO 7: Configuración de Git Individual

Cada compañero debe configurar su Git local:

```bash
# Configurar nombre y email (información personal de cada uno)
git config user.name "Tu Nombre"
git config user.email "tu.email@ejemplo.com"

# Verificar configuración
git config --list
```

**Esto es importante para que los commits muestren quién hizo cada cambio.**

---

## 🚨 Problemas Comunes y Soluciones

### Problema 1: "Falta el archivo .env"

**Solución:**
```bash
copy .env.example .env
# Luego editar .env con credenciales reales
```

### Problema 2: "Credenciales incorrectas"

**Solución:**
- Verificar que copiaste bien las credenciales de `CREDENTIALS.md`
- No debe haber espacios extra
- Verificar que no quedaron los placeholders (`TU_PASSWORD_AQUI`)

### Problema 3: "Login no funciona"

**Solución:**
```bash
# Verificar conexión a base de datos
python manage.py dbshell
# Si conecta, escribir \q para salir
```

### Problema 4: "Conflictos al hacer git pull"

**Solución:**
```bash
# Si tienen cambios locales
git stash  # Guardar cambios temporalmente
git pull origin main
git stash pop  # Recuperar cambios
```

---

## 📊 Checklist Final

### Para ti (antes de subir):
- [ ] Verificar que `.env` NO está en los archivos a subir
- [ ] Verificar que `CREDENTIALS.md` NO está en los archivos a subir (o está en .gitignore)
- [ ] Verificar que `.env.example` NO tiene contraseñas reales
- [ ] Hacer commit con mensaje descriptivo
- [ ] Hacer push a GitHub
- [ ] Compartir `CREDENTIALS.md` por canal seguro

### Para tus compañeros (después de actualizar):
- [ ] `git pull origin main`
- [ ] Crear archivo `.env` desde `.env.example`
- [ ] Copiar credenciales reales de `CREDENTIALS.md` a `.env`
- [ ] `python manage.py check` (sin errores)
- [ ] `python manage.py runserver 8001` (funciona)
- [ ] Probar login en navegador
- [ ] Configurar su Git local con su nombre/email

---

## 🎯 Resumen Ejecutivo

**Lo que DEBES subir a GitHub:**
✅ `.env.example` (limpio, sin credenciales)
✅ `SETUP_GUIDE.md`
✅ `DOCUMENTACION_AUTENTICACION.md`
✅ `GUIA_COMPLETA_RECUPERACION_PASSWORD.md`
✅ Código del proyecto

**Lo que NO DEBES subir:**
❌ `.env` (ya está en .gitignore)
❌ `CREDENTIALS.md` (tiene contraseñas reales)
❌ `db.sqlite3` (si existe)
❌ `__pycache__/`

**Lo que debes compartir por otro medio:**
📧 `CREDENTIALS.md` → Discord/WhatsApp/Drive privado

---

## 🆘 Soporte

Si tus compañeros tienen problemas:
1. Que revisen `SETUP_GUIDE.md`
2. Que verifiquen que su `.env` tiene las credenciales correctas
3. Que ejecuten `python manage.py check` para ver errores específicos
4. Que te contacten con el error exacto

---

**¡Listo!** Con estos pasos, tu equipo podrá trabajar sin problemas. 🚀
