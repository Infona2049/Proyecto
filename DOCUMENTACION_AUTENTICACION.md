# 📚 Documentación Técnica: Sistema de Autenticación y Seguridad - EcoFact

## 🎯 Resumen Ejecutivo

El proyecto **EcoFact** utiliza el sistema de autenticación nativo de **Django** (Django Auth) con extensiones personalizadas para seguridad adicional. **NO usa JWT ni OAuth 2.0**, sino que se basa en **sesiones del lado del servidor** con cookies.

---

## 🔐 1. Sistema de Autenticación (Login)

### Tecnología Base
- **Framework:** Django 5.2.4
- **Sistema:** Django Authentication System (basado en sesiones)
- **Modelo de Usuario:** `AbstractUser` personalizado

### Arquitectura del Login

#### 1.1 Modelo de Usuario Personalizado

```python
class Usuario(AbstractUser):
    # Campos personalizados
    correo_electronico_usuario = models.EmailField(unique=True)
    rol_usuario = models.CharField(choices=ROL_USUARIO_CHOICES)
    
    # Campos de seguridad
    intentos_fallidos = models.IntegerField(default=0)
    bloqueado_hasta = models.DateTimeField(null=True, blank=True)
    ultimo_intento_fallido = models.DateTimeField(null=True, blank=True)
    
    USERNAME_FIELD = 'correo_electronico_usuario'  # Login con email
```

**Características:**
- ✅ Hereda de `AbstractUser` (modelo base de Django)
- ✅ Autenticación por **email** en lugar de username
- ✅ Sistema de roles: Admin, Vendedor, Cliente
- ✅ Campos adicionales para control de intentos fallidos

---

#### 1.2 Flujo de Login

**Ubicación:** [`core/views.py:41-120`](file:///C:/Users/juand/.gemini/antigravity/scratch/Proyecto/core/views.py#L41-L120)

```python
def login_view(request):
    # 1. Recibir credenciales (email + password)
    email = request.POST.get('email')
    password = request.POST.get('password')
    
    # 2. Buscar usuario por email
    usuario = Usuario.objects.get(correo_electronico_usuario=email)
    
    # 3. Verificar si está bloqueado
    if usuario.esta_bloqueado():
        return JsonResponse({'bloqueado': True, 'tiempo_restante': X})
    
    # 4. Autenticar con Django Auth
    user = authenticate(request, username=email, password=password)
    
    # 5. Si es exitoso
    if user is not None:
        usuario.resetear_intentos_fallidos()
        login(request, user)  # Crea sesión
        return redirect_segun_rol(user)
    
    # 6. Si falla
    else:
        usuario.incrementar_intentos_fallidos()
        if intentos >= 3:
            bloquear_por_10_minutos()
```

**Características de Seguridad:**

1. **Protección contra Fuerza Bruta:**
   - Máximo 3 intentos fallidos
   - Bloqueo automático por 10 minutos
   - Contador de intentos por usuario

2. **Mensajes Genéricos:**
   - No revela si el email existe o no
   - Siempre dice "Credenciales incorrectas"

3. **Sesiones del Servidor:**
   - Django crea una sesión en el servidor
   - Cookie `sessionid` enviada al cliente
   - No expone información sensible en el cliente

---

### 1.3 Almacenamiento de Contraseñas

**Método:** Django Password Hashing (PBKDF2 por defecto)

```python
# Al crear usuario
usuario.set_password('contraseña_plana')  # Hash automático
usuario.save()

# Al verificar
user = authenticate(username=email, password=password)  # Compara hashes
```

**Algoritmo de Hash:**
- **PBKDF2** con SHA256
- **260,000 iteraciones** (Django 5.2)
- **Salt aleatorio** por contraseña
- Formato: `pbkdf2_sha256$260000$salt$hash`

**Ejemplo de hash almacenado:**
```
pbkdf2_sha256$260000$abc123xyz$Hj8kL2mN9pQ4rS5tU6vW7xY8zA1bC2dE3fG4hI5jK6
```

---

## 🔑 2. Sistema de Recuperación de Contraseña

### Tecnología
- **Método:** Código de verificación de 6 dígitos
- **Envío:** Email SMTP (Gmail)
- **Validez:** 10 minutos
- **Almacenamiento:** Base de datos PostgreSQL (Neon)

### Flujo Completo

#### 2.1 Solicitar Código

**Ubicación:** [`core/views.py:285-713`](file:///C:/Users/juand/.gemini/antigravity/scratch/Proyecto/core/views.py#L285-L713)

```python
@csrf_exempt
@require_http_methods(["POST"])
def enviar_codigo_recuperacion(request):
    # 1. Recibir email del usuario
    email = data.get('email')
    
    # 2. Verificar que el usuario existe
    usuario = Usuario.objects.get(correo_electronico_usuario=email)
    
    # 3. Generar código aleatorio de 6 dígitos
    codigo = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    
    # 4. Guardar en base de datos
    CodigoRecuperacion.objects.create(email=email, codigo=codigo)
    
    # 5. Enviar email con diseño profesional
    send_email_with_html_template(email, codigo, usuario.nombre)
    
    return JsonResponse({'status': 'ok'})
```

**Modelo de Código:**
```python
class CodigoRecuperacion(models.Model):
    email = models.EmailField()
    codigo = models.CharField(max_length=6)
    creado_en = models.DateTimeField(auto_now_add=True)
    usado = models.BooleanField(default=False)
    
    def es_valido(self):
        # Válido por 10 minutos y no usado
        tiempo_expiracion = self.creado_en + timedelta(minutes=10)
        return not self.usado and timezone.now() < tiempo_expiracion
```

---

#### 2.2 Verificar Código

**Ubicación:** [`core/views.py:715-764`](file:///C:/Users/juand/.gemini/antigravity/scratch/Proyecto/core/views.py#L715-L764)

```python
def verificar_codigo_recuperacion(request):
    # 1. Recibir email y código
    email = data.get('email')
    codigo = data.get('codigo')
    
    # 2. Buscar código más reciente
    codigo_obj = CodigoRecuperacion.objects.filter(
        email=email, 
        codigo=codigo
    ).order_by('-creado_en').first()
    
    # 3. Validar
    if not codigo_obj or not codigo_obj.es_valido():
        return error('Código inválido o expirado')
    
    return success('Código verificado')
```

---

#### 2.3 Restablecer Contraseña

**Ubicación:** [`core/views.py:766-821`](file:///C:/Users/juand/.gemini/antigravity/scratch/Proyecto/core/views.py#L766-L821)

```python
def restablecer_contrasena(request):
    # 1. Verificar código nuevamente
    if not codigo_obj.es_valido():
        return error('Código expirado')
    
    # 2. Actualizar contraseña
    usuario = Usuario.objects.get(correo_electronico_usuario=email)
    usuario.set_password(nueva_password)  # Hash automático
    usuario.save()
    
    # 3. Marcar código como usado
    codigo_obj.usado = True
    codigo_obj.save()
    
    return success('Contraseña actualizada')
```

---

### 2.4 Email de Recuperación

**Configuración SMTP:**
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'ecofactproyect@gmail.com'
EMAIL_HOST_PASSWORD = 'App Password de Gmail'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
```

**Características del Email:**
- ✅ Diseño HTML profesional con CSS inline
- ✅ Logos embebidos (EcoFact + Apple Pereira)
- ✅ Código destacado visualmente
- ✅ Advertencias de seguridad
- ✅ Responsive design

---

## 🛡️ 3. Medidas de Seguridad Implementadas

### 3.1 Protección contra Ataques

| Ataque | Protección | Implementación |
|--------|-----------|----------------|
| **Fuerza Bruta** | Bloqueo temporal | 3 intentos → 10 min bloqueado |
| **CSRF** | Token CSRF | `CsrfViewMiddleware` activo |
| **XSS** | Escape automático | Templates de Django |
| **SQL Injection** | ORM de Django | Queries parametrizadas |
| **Session Hijacking** | Cookies seguras | `SESSION_COOKIE_HTTPONLY=True` |
| **Clickjacking** | X-Frame-Options | `XFrameOptionsMiddleware` |

### 3.2 Seguridad de Sesiones

**Configuración:**
```python
# En settings.py (valores por defecto de Django)
SESSION_COOKIE_HTTPONLY = True  # No accesible desde JavaScript
SESSION_COOKIE_SECURE = False   # True en producción (HTTPS)
SESSION_COOKIE_SAMESITE = 'Lax' # Protección CSRF
SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # Sesiones en BD
```

**Ciclo de Vida:**
1. Usuario hace login → Django crea sesión en BD
2. Cookie `sessionid` enviada al navegador
3. Cada request incluye cookie → Django valida sesión
4. Logout → Sesión eliminada de BD

---

### 3.3 Control de Acceso por Roles

**Decorador Personalizado:**
```python
@role_required(['admin', 'vendedor'])
def crear_factura_view(request):
    # Solo admin y vendedor pueden acceder
    return render(request, 'facturas/crear_factura.html')
```

**Middleware de Redirección:**
```python
class RoleRedirectMiddleware:
    # Redirige automáticamente según el rol después del login
    # Admin → /admin-dashboard/
    # Vendedor → /vendedor-dashboard/
    # Cliente → /cliente-dashboard/
```

---

## 🔄 4. Comparación con Otros Sistemas

### Django Sessions vs JWT

| Característica | Django Sessions (EcoFact) | JWT |
|----------------|---------------------------|-----|
| **Almacenamiento** | Servidor (PostgreSQL) | Cliente (localStorage/cookie) |
| **Revocación** | ✅ Inmediata | ❌ Difícil (hasta expiración) |
| **Escalabilidad** | Requiere BD compartida | ✅ Stateless |
| **Seguridad** | ✅ Más seguro (servidor) | Depende de implementación |
| **Complejidad** | ✅ Simple (built-in Django) | Requiere librerías adicionales |
| **Uso típico** | Apps monolíticas | APIs REST, microservicios |

**¿Por qué Django Sessions?**
- ✅ Proyecto monolítico (no API separada)
- ✅ Revocación inmediata de sesiones
- ✅ Menos complejidad
- ✅ Built-in en Django (no dependencias extra)

---

### Django Sessions vs OAuth 2.0

| Característica | Django Sessions | OAuth 2.0 |
|----------------|-----------------|-----------|
| **Propósito** | Autenticación interna | Autenticación delegada |
| **Uso típico** | App propia | Login con Google/Facebook |
| **Complejidad** | ✅ Baja | Alta |
| **Dependencias** | Ninguna | Proveedor externo |

**OAuth 2.0 no es necesario** porque:
- No hay login con redes sociales
- No hay integración con servicios externos
- Usuarios propios del sistema

---

## 📊 5. Diagrama de Flujo

### Login Flow

```
Usuario ingresa email/password
         ↓
¿Usuario existe? → NO → "Credenciales incorrectas"
         ↓ SÍ
¿Está bloqueado? → SÍ → "Bloqueado por X minutos"
         ↓ NO
Django authenticate()
         ↓
¿Password correcto? → NO → Incrementar intentos → ¿3 intentos? → Bloquear
         ↓ SÍ
Resetear intentos
         ↓
Crear sesión (login())
         ↓
Redirigir según rol
```

### Password Recovery Flow

```
Usuario ingresa email
         ↓
Generar código 6 dígitos
         ↓
Guardar en BD (válido 10 min)
         ↓
Enviar email con código
         ↓
Usuario ingresa código
         ↓
¿Código válido? → NO → "Código inválido/expirado"
         ↓ SÍ
Usuario ingresa nueva contraseña
         ↓
Hash contraseña (PBKDF2)
         ↓
Actualizar en BD
         ↓
Marcar código como usado
         ↓
"Contraseña actualizada"
```

---

## 🔧 6. Configuración de Seguridad

### Variables de Entorno Críticas

```bash
# Django
SECRET_KEY=clave_secreta_para_firmar_cookies_y_tokens
DEBUG=False  # SIEMPRE False en producción

# Base de Datos
DB_PASSWORD=contraseña_segura_neon

# Email
EMAIL_HOST_PASSWORD=app_password_gmail
```

### Recomendaciones para Producción

1. **HTTPS Obligatorio:**
   ```python
   SECURE_SSL_REDIRECT = True
   SESSION_COOKIE_SECURE = True
   CSRF_COOKIE_SECURE = True
   ```

2. **Headers de Seguridad:**
   ```python
   SECURE_HSTS_SECONDS = 31536000
   SECURE_HSTS_INCLUDE_SUBDOMAINS = True
   SECURE_CONTENT_TYPE_NOSNIFF = True
   SECURE_BROWSER_XSS_FILTER = True
   ```

3. **Rotación de SECRET_KEY:**
   - Cambiar cada 6 meses
   - Usar generador seguro: `get_random_secret_key()`

---

## 📝 7. Resumen para Presentación

### Puntos Clave

**Sistema de Autenticación:**
- ✅ Django Authentication System (basado en sesiones)
- ✅ Login con email + contraseña
- ✅ Contraseñas hasheadas con PBKDF2-SHA256
- ✅ Sesiones almacenadas en PostgreSQL (Neon)
- ✅ Protección contra fuerza bruta (3 intentos → bloqueo 10 min)

**Recuperación de Contraseña:**
- ✅ Código de 6 dígitos enviado por email
- ✅ Válido por 10 minutos
- ✅ Un solo uso por código
- ✅ Email profesional con HTML/CSS

**Seguridad:**
- ✅ Protección CSRF (tokens)
- ✅ Protección XSS (escape automático)
- ✅ Protección SQL Injection (ORM)
- ✅ Control de acceso por roles
- ✅ Cookies HttpOnly (no accesibles desde JS)

**NO utiliza:**
- ❌ JWT (no es necesario para app monolítica)
- ❌ OAuth 2.0 (no hay login con redes sociales)
- ❌ Autenticación de dos factores (2FA) - podría agregarse

---

## 🎓 Conclusión

El sistema de autenticación de EcoFact es **robusto y apropiado** para una aplicación web monolítica de facturación electrónica. Utiliza las mejores prácticas de Django y proporciona múltiples capas de seguridad sin agregar complejidad innecesaria.

**Fortalezas:**
- Simple y mantenible
- Seguro por defecto (Django best practices)
- Protección contra ataques comunes
- Recuperación de contraseña user-friendly

**Posibles Mejoras Futuras:**
- Autenticación de dos factores (2FA)
- Login con redes sociales (OAuth 2.0)
- Auditoría de accesos (logs de login)
- Políticas de contraseñas más estrictas
