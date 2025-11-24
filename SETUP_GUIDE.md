# 🚀 Guía de Configuración para Nuevos Miembros - EcoFact

Esta guía te ayudará a configurar el proyecto en tu máquina local paso a paso.

---

## ✅ Requisitos Previos

- Python 3.11 o superior instalado
- Git instalado
- Acceso al repositorio de GitHub
- **Credenciales del proyecto** (solicítalas al líder del equipo)

---

## 📦 Instalación Paso a Paso

### 1. Clonar el Repositorio

```bash
git clone https://github.com/Infona2049/Proyecto.git
cd Proyecto
```

### 2. Crear Entorno Virtual

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

#### ⚠️ PASO CRÍTICO - NO OMITIR

```bash
# Copiar el archivo de ejemplo
copy .env.example .env
```

Ahora **DEBES** editar el archivo `.env` y reemplazar los placeholders con las credenciales reales:

1. Abre `.env` con tu editor de texto
2. **Solicita las credenciales al líder del equipo** (archivo `CREDENTIALS.md`)
3. Reemplaza:
   - `TU_PASSWORD_DE_NEON_AQUI` → contraseña real de Neon
   - `TU_SECRET_KEY_AQUI` → SECRET_KEY del proyecto
   - `TU_EMAIL_AQUI@gmail.com` → email del proyecto
   - `TU_APP_PASSWORD_DE_GMAIL_AQUI` → App Password de Gmail

**Ejemplo de `.env` configurado correctamente:**

```bash
USE_POSTGRESQL=True
DB_NAME=neondb
DB_USER=neondb_owner
DB_PASSWORD=npg_lXCDaqE7I5wh  # ← Credencial real, NO placeholder
DB_HOST=ep-divine-base-abk7yom6-pooler.eu-west-2.aws.neon.tech
DB_PORT=5432

SECRET_KEY=bgmcb%-*eu*np3_+jxb81d4!k_v@ws6qo3au(egm73i65f1ov_  # ← Credencial real

DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

EMAIL_HOST_USER=ecofactproyect@gmail.com  # ← Email real
EMAIL_HOST_PASSWORD=ynoffupvodsyozjl  # ← App Password real
# ... resto de configuración de email
```

### 5. Ejecutar el Servidor

```bash
python manage.py runserver 8001
```

### 6. Verificar que Funciona

Abre tu navegador en: `http://localhost:8001/`

**Usuarios de prueba:**
- **Admin:** admin@ecofact.com / admin123
- **Vendedor:** vendedor@ecofact.com / vendedor123
- **Cliente:** cliente@ecofact.com / cliente123

---

## 🔧 Configuración de Git (Recomendado)

Para evitar conflictos en el equipo, configura tu Git local:

```bash
# Configurar tu nombre y email (usa tu información personal)
git config user.name "Tu Nombre"
git config user.email "tu.email@ejemplo.com"

# Verificar configuración
git config --list
```

---

## ❌ Errores Comunes y Soluciones

### Error: "Falta el archivo .env o la variable SECRET_KEY"

**Causa:** No creaste el archivo `.env` o está vacío

**Solución:**
```bash
copy .env.example .env
# Luego edita .env con las credenciales reales
```

---

### Error: "Falta la configuración de PostgreSQL en .env"

**Causa:** No reemplazaste `TU_PASSWORD_DE_NEON_AQUI` con la contraseña real

**Solución:**
1. Solicita el archivo `CREDENTIALS.md` al líder del equipo
2. Copia la contraseña real de Neon
3. Reemplaza en tu archivo `.env`

---

### Error: "Falta la configuración de Email en .env"

**Causa:** No configuraste las credenciales de Gmail

**Solución:**
1. Solicita las credenciales de email al líder del equipo
2. Reemplaza `TU_APP_PASSWORD_DE_GMAIL_AQUI` con el App Password real

---

### Login no funciona / Credenciales incorrectas

**Posibles causas:**
1. No estás conectado a la base de datos Neon
2. Las credenciales de la BD son incorrectas

**Solución:**
```bash
# Verificar conexión a la base de datos
python manage.py dbshell
# Si se conecta, escribe \q para salir
# Si da error, revisa las credenciales de DB en .env
```

---

### Puerto 8001 ocupado

**Solución:**
```bash
# Usa otro puerto
python manage.py runserver 8002
```

---

## 📚 Estructura del Proyecto

```
Proyecto/
├── core/                   # App principal (usuarios, auth)
├── productos/              # Gestión de productos
├── facturas/               # Gestión de facturas
├── static/                 # Archivos estáticos (CSS, JS, imágenes)
├── EcoFactProject/         # Configuración del proyecto
│   └── settings.py        # Configuración principal
├── .env                    # ⚠️ TUS CREDENCIALES (NO SUBIR A GIT)
├── .env.example            # Plantilla de configuración
├── .gitignore              # Archivos ignorados por Git
├── requirements.txt        # Dependencias de Python
└── manage.py               # Script de gestión de Django
```

---

## 🔐 Seguridad - MUY IMPORTANTE

### ✅ Lo que SÍ debes hacer:
- Crear tu archivo `.env` local
- Guardar las credenciales en un lugar seguro
- Usar las credenciales compartidas por el equipo

### ❌ Lo que NO debes hacer:
- **NUNCA** subir el archivo `.env` a GitHub
- **NUNCA** compartir credenciales en lugares públicos
- **NUNCA** hacer commit de archivos con contraseñas

### Verificar antes de hacer commit:

```bash
# Ver qué archivos vas a subir
git status

# Si ves .env en la lista, NO HAGAS COMMIT
# El .env debe estar en .gitignore
```

---

## 🆘 ¿Necesitas Ayuda?

1. **Revisa esta guía** - La mayoría de problemas están documentados aquí
2. **Verifica tu `.env`** - 90% de los problemas son por configuración incorrecta
3. **Contacta al equipo** - Si nada funciona, pide ayuda

---

## 🎯 Checklist de Configuración Exitosa

- [ ] Repositorio clonado
- [ ] Entorno virtual creado y activado
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Archivo `.env` creado desde `.env.example`
- [ ] Credenciales reales copiadas en `.env` (sin placeholders)
- [ ] Servidor ejecutándose sin errores (`python manage.py runserver 8001`)
- [ ] Login funciona con usuarios de prueba
- [ ] Git configurado con tu nombre y email

---

**¡Listo!** Si completaste todos los pasos, ya puedes empezar a trabajar en el proyecto. 🎉
