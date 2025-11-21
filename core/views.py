from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Q
from functools import wraps
import json
from .forms import RegistroUsuarioForm
from .models import Usuario, CodigoRecuperacion

def role_required(allowed_roles):
    """Decorador para restringir acceso por roles"""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            # Redirigir a dashboard correspondiente si no tiene permisos
            if request.user.rol_usuario not in allowed_roles:
                messages.error(request, 'No tienes permisos para acceder a esta página')
                
                # Redirigir al dashboard correcto según el rol
                if request.user.rol_usuario == 'admin':
                    return redirect('admin_dashboard')
                elif request.user.rol_usuario == 'vendedor':
                    return redirect('vendedor_dashboard')
                elif request.user.rol_usuario == 'cliente':
                    return redirect('cliente_dashboard')
                else:
                    return redirect('login')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Buscar el usuario por email
        try:
            usuario = Usuario.objects.get(correo_electronico_usuario=email)
        except Usuario.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Credenciales incorrectas'
            })
        
        # Verificar si el usuario está bloqueado
        if usuario.esta_bloqueado():
            tiempo_restante = usuario.bloqueado_hasta - timezone.now()
            minutos_restantes = int(tiempo_restante.total_seconds() / 60)
            return JsonResponse({
                'success': False,
                'message': f'Usuario bloqueado. Intenta de nuevo en {minutos_restantes} minutos.',
                'bloqueado': True,
                'tiempo_restante': minutos_restantes
            })
        
        # Autenticar usuario
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            # Login exitoso - resetear intentos fallidos
            usuario.resetear_intentos_fallidos()
            login(request, user)
            
            # Redirigir según el rol del usuario
            if user.is_superuser:
                return JsonResponse({
                    'success': True,
                    'message': 'Bienvenido Superadmin',
                    'redirect_url': '/admin/'
                })
            elif user.rol_usuario == 'admin':
                return JsonResponse({
                    'success': True,
                    'message': 'Bienvenido Administrador',
                    'redirect_url': '/admin-dashboard/'
                })
            elif user.rol_usuario == 'vendedor':
                return JsonResponse({
                    'success': True,
                    'message': 'Bienvenido Vendedor',
                    'redirect_url': '/vendedor-dashboard/'
                })
            elif user.rol_usuario == 'cliente':
                return JsonResponse({
                    'success': True,
                    'message': 'Bienvenido Cliente',
                    'redirect_url': '/cliente-dashboard/'
                })
        else:
            # Login fallido - incrementar intentos
            usuario.incrementar_intentos_fallidos()
            
            intentos_restantes = 3 - usuario.intentos_fallidos
            
            if usuario.intentos_fallidos >= 3:
                return JsonResponse({
                    'success': False,
                    'message': 'Credenciales incorrectas. Usuario bloqueado por 10 minutos.',
                    'bloqueado': True,
                    'intentos_restantes': 0
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': f'Credenciales incorrectas. Te quedan {intentos_restantes} intentos.',
                    'intentos_restantes': intentos_restantes
                })
    
    # Si es GET, mostrar el formulario de login
    return render(request, 'core/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente')
    return redirect('login')

@role_required(['admin'])
def admin_dashboard_view(request):
    return render(request, 'core/visualizacion_Admin.html')

@role_required(['vendedor'])
def vendedor_dashboard_view(request):
    return render(request, 'core/visualizacion_Vendedor.html')

@role_required(['cliente'])
def cliente_dashboard_view(request):
    return render(request, 'core/visualizacion_Cliente.html')

@login_required
def documentos_view(request):
    return render(request, 'core/documentos.html')

@login_required
def actualizar_perfil_view(request):
    return render(request, 'core/actualizar_perfil.html')

def cambiocontraseña_view(request):
    return render(request, 'core/olvido_contraseña.html')

def acerca_nosotros_view(request):
    return render(request, 'core/acerca_nosotros.html')

@role_required(['admin', 'vendedor'])
def historial_factura_view(request):
    return render(request, 'facturas/historial_factura.html')

@role_required(['admin', 'vendedor'])
def crear_factura_view(request):
    return render(request, 'facturas/crear_factura.html')

def olvido_contraseña_view(request):
    return render(request, 'core/olvido_contraseña.html')

def registro_view(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            try:
                # Guardar el usuario
                user = form.save()
                
                # Mensaje de éxito
                messages.success(request, 'Usuario registrado exitosamente. Ya puedes iniciar sesión.')
                
                # Redirigir al login
                return redirect('login')
                
            except Exception as e:
                messages.error(request, f'Error al registrar usuario: {str(e)}')
        else:
            # Si hay errores en el formulario, mostrarlos
            for field, errors in form.errors.items():
                field_label = form.fields[field].label or field
                for error in errors:
                    messages.error(request, f'{field_label}: {error}')
    else:
        form = RegistroUsuarioForm()
    
    return render(request, 'core/registro.html', {'form': form})

@role_required(['admin'])
def visualizacion_admin_view(request):
    return render(request, 'core/visualizacion_Admin.html')

@role_required(['cliente'])
def visualizacion_cliente_view(request):
    return render(request, 'core/visualizacion_Cliente.html')

@role_required(['vendedor'])
def visualizacion_vendedor_view(request):
    return render(request, 'core/visualizacion_Vendedor.html')


# ============================================================================
# RECUPERACIÓN DE CONTRASEÑA
# ============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def enviar_codigo_recuperacion(request):
    """Envía un código de recuperación al correo del usuario"""
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()
        
        print(f"\n🔍 DEBUG: Email recibido del frontend: '{email}'")
        
        if not email:
            print("❌ Email vacío")
            return JsonResponse({'status': 'error', 'message': 'El correo es obligatorio'}, status=400)
        
        # Verificar que el usuario existe
        try:
            usuario = Usuario.objects.get(correo_electronico_usuario=email)
            print(f"✅ Usuario encontrado: {usuario.nombre_usuario} (PK: {usuario.pk})")
        except Usuario.DoesNotExist:
            print(f"❌ Usuario NO encontrado con email: '{email}'")
            print("📋 Verificando todos los emails en la BD...")
            todos_emails = Usuario.objects.values_list('correo_electronico_usuario', 'nombre_usuario')
            for db_email, nombre in todos_emails:
                print(f"   - '{db_email}' ({nombre})")
            # Por seguridad, no revelar si el correo existe o no
            return JsonResponse({'status': 'ok', 'message': 'Si el correo existe, recibirás un código'})
        
        # Generar código de 6 dígitos
        import random
        codigo = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        
        # Guardar código en la base de datos
        CodigoRecuperacion.objects.create(
            email=email,
            codigo=codigo
        )
        
        # Enviar correo con el código
        from django.core.mail import EmailMultiAlternatives, send_mail
        from django.conf import settings
        
        print(f"\n🔍 INICIANDO ENVÍO DE EMAIL")
        print(f"Email destino: {email}")
        print(f"Código: {codigo}")
        print(f"Usuario encontrado: {usuario.nombre_usuario}")
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 40px 20px;
                    line-height: 1.6;
                }}
                .email-wrapper {{
                    max-width: 650px;
                    margin: 0 auto;
                    background-color: white;
                    border-radius: 20px;
                    overflow: hidden;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                }}
                .header {{
                    background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
                    padding: 40px 30px;
                    text-align: center;
                    border-bottom: 5px solid #fbbf24;
                }}
                .logo-container {{
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    gap: 30px;
                    margin-bottom: 20px;
                    border: none;
                }}
                .logo {{
                    max-width: 80px;
                    height: auto;
                }}
                .header h1 {{
                    color: #1e3a8a;
                    font-size: 28px;
                    font-weight: 700;
                    margin: 0;
                    text-transform: uppercase;
                    letter-spacing: 2px;
                }}
                .header p {{
                    color: #475569;
                    font-size: 14px;
                    margin-top: 8px;
                }}
                .content {{
                    padding: 50px 40px;
                    background-color: #ffffff;
                }}
                .greeting {{
                    font-size: 18px;
                    color: #1f2937;
                    margin-bottom: 20px;
                }}
                .greeting strong {{
                    color: #1e40af;
                    font-size: 20px;
                }}
                .message {{
                    color: #4b5563;
                    font-size: 16px;
                    margin-bottom: 30px;
                    line-height: 1.8;
                }}
                .code-section {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border-radius: 15px;
                    padding: 40px;
                    text-align: center;
                    margin: 35px 0;
                    box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
                    position: relative;
                    overflow: hidden;
                }}
                .code-section::before {{
                    content: '';
                    position: absolute;
                    top: -50%;
                    right: -50%;
                    width: 200%;
                    height: 200%;
                    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
                    animation: pulse 3s ease-in-out infinite;
                }}
                @keyframes pulse {{
                    0%, 100% {{ transform: scale(1); }}
                    50% {{ transform: scale(1.1); }}
                }}
                .code-label {{
                    color: #e0e7ff;
                    font-size: 14px;
                    text-transform: uppercase;
                    letter-spacing: 2px;
                    margin-bottom: 15px;
                    font-weight: 600;
                }}
                .code {{
                    font-size: 56px;
                    font-weight: 900;
                    color: #ffffff;
                    letter-spacing: 18px;
                    margin: 20px 0;
                    text-shadow: 0 4px 15px rgba(0,0,0,0.3);
                    position: relative;
                    z-index: 1;
                    font-family: 'Courier New', monospace;
                }}
                .code-validity {{
                    color: #fbbf24;
                    font-size: 13px;
                    font-weight: 600;
                    margin-top: 15px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 8px;
                }}
                .code-validity::before {{
                    content: '⏱';
                    font-size: 18px;
                }}
                .warning-box {{
                    background: linear-gradient(to right, #fef3c7, #fde68a);
                    border-left: 6px solid #f59e0b;
                    border-radius: 12px;
                    padding: 25px;
                    margin: 30px 0;
                    box-shadow: 0 4px 15px rgba(245, 158, 11, 0.2);
                }}
                .warning-box h3 {{
                    color: #92400e;
                    font-size: 16px;
                    margin-bottom: 12px;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }}
                .warning-box h3::before {{
                    content: '⚠️';
                    font-size: 20px;
                }}
                .warning-box ul {{
                    list-style: none;
                    margin: 0;
                    padding: 0;
                }}
                .warning-box li {{
                    color: #92400e;
                    font-size: 14px;
                    margin: 8px 0;
                    padding-left: 20px;
                    position: relative;
                }}
                .warning-box li::before {{
                    content: '•';
                    position: absolute;
                    left: 0;
                    color: #f59e0b;
                    font-size: 20px;
                    line-height: 1;
                }}
                .help-section {{
                    background-color: #f0f9ff;
                    border-radius: 12px;
                    padding: 20px;
                    margin: 30px 0;
                    text-align: center;
                    border: 2px solid #bfdbfe;
                }}
                .help-section p {{
                    color: #1e40af;
                    font-size: 14px;
                    margin: 0;
                }}
                .footer {{
                    background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
                    padding: 35px 30px;
                    text-align: center;
                }}
                .footer-logos {{
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    gap: 30px;
                    margin-bottom: 20px;
                    border: none;
                }}
                .footer-logo {{
                    max-width: 70px;
                    height: auto;
                    opacity: 0.9;
                }}
                .footer h3 {{
                    color: #1e3a8a;
                    font-size: 18px;
                    margin-bottom: 10px;
                    font-weight: 700;
                }}
                .footer p {{
                    color: #000000;
                    font-size: 13px;
                    margin: 8px 0;
                }}
                .footer .contact {{
                    color: #1e40af;
                    font-size: 14px;
                    margin: 15px 0 10px;
                    font-weight: 600;
                }}
                .divider {{
                    height: 1px;
                    background: linear-gradient(to right, transparent, #374151, transparent);
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <div class="email-wrapper">
                <!-- Header con logos -->
                <div class="header">
                    <div class="logo-container">
                        <img src="cid:logo_ecofact" alt="EcoFact Logo" class="logo">
                        <img src="cid:logo_apple" alt="Apple Pereira Logo" class="logo">
                    </div>
                    <h1>🔐 Recuperación de Contraseña</h1>
                    <p>Sistema de Seguridad EcoFact</p>
                </div>
                
                <!-- Contenido principal -->
                <div class="content">
                    <div class="greeting">
                        Hola <strong>{usuario.nombre_usuario}</strong>,
                    </div>
                    
                    <p class="message">
                        Recibimos una solicitud para restablecer la contraseña de tu cuenta en EcoFact.
                        Por tu seguridad, hemos generado un código de verificación único que deberás ingresar
                        para continuar con el proceso de recuperación.
                    </p>
                    
                    <!-- Sección del código -->
                    <div class="code-section">
                        <div class="code-label">Tu código de verificación es:</div>
                        <div class="code">{codigo}</div>
                        <div class="code-validity">Válido por 10 minutos</div>
                    </div>
                    
                    <!-- Advertencias -->
                    <div class="warning-box">
                        <h3>Información Importante</h3>
                        <ul>
                            <li>Este código es válido únicamente por <strong>10 minutos</strong></li>
                            <li>No compartas este código con nadie, ni siquiera con personal de EcoFact</li>
                            <li>Si no solicitaste este cambio, ignora este correo y tu cuenta permanecerá segura</li>
                            <li>Después de usar el código, será inválido automáticamente</li>
                        </ul>
                    </div>
                    
                </div>
                
                <!-- Footer -->
                <div class="footer">
                    <div class="footer-logos">
                        <img src="cid:logo_ecofact" alt="EcoFact" class="footer-logo">
                        <img src="cid:logo_apple" alt="Apple Pereira" class="footer-logo">
                    </div>
                    <h3>EcoFact</h3>
                    <p>Sistema de Facturación Electrónica</p>
                    <p style="margin: 15px 0; font-size: 14px;">¿Tienes problemas? Contáctanos:</p>
                    <p class="contact">📧 ecofactproyect@gmail.com | 📞 333-333-333</p>
                    <p>Este es un correo automático, por favor no responder directamente.</p>
                    <p>© 2025 EcoFact. Todos los derechos reservados.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Recuperación de Contraseña - EcoFact
        
        Hola {usuario.nombre_usuario},
        
        Tu código de verificación es: {codigo}
        
        Este código es válido por 10 minutos.
        
        Si no solicitaste este cambio, ignora este correo.
        
        EcoFact - Sistema de Facturación Electrónica
        """
        
        subject = 'Código de Recuperación - EcoFact'
        from_email = settings.EMAIL_HOST_USER
        to_email = [email]
        
        # Debug: Información de configuración de email
        print("\n" + "="*60)
        print("📧 DEBUG - ENVÍO DE EMAIL DE RECUPERACIÓN")
        print("="*60)
        print(f"De: {from_email}")
        print(f"Para: {to_email}")
        print(f"Asunto: {subject}")
        print(f"Código generado: {codigo}")
        print(f"Usuario: {usuario.nombre_usuario}")
        print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
        print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
        print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
        print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
        print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
        password = settings.EMAIL_HOST_PASSWORD
        print(f"EMAIL_HOST_PASSWORD configurado: {'Sí' if password else 'No'} (primeros 4 chars: {password[:4] if password else 'N/A'})")
        print("="*60 + "\n")
        
        # Enviar email con HTML y logos
        print("📤 Enviando email con diseño profesional...")
        msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        msg.attach_alternative(html_content, "text/html")
        
        # Adjuntar logos como imágenes embebidas
        import os
        from django.conf import settings as django_settings
        from email.mime.image import MIMEImage
        
        # Ruta de los logos
        logo_ecofact_path = os.path.join(django_settings.BASE_DIR, 'static', 'img', 'Logo azul sin fondo.png')
        logo_apple_path = os.path.join(django_settings.BASE_DIR, 'static', 'img', 'logo empresa.png')
        
        print(f"📁 Buscando logos en:")
        print(f"   EcoFact: {logo_ecofact_path}")
        print(f"   Apple: {logo_apple_path}")
        
        # Adjuntar logo EcoFact
        try:
            with open(logo_ecofact_path, 'rb') as img:
                logo_ecofact = MIMEImage(img.read())
                logo_ecofact.add_header('Content-ID', '<logo_ecofact>')
                logo_ecofact.add_header('Content-Disposition', 'inline', filename='logo_ecofact.png')
                msg.attach(logo_ecofact)
                print("✅ Logo EcoFact adjuntado")
        except Exception as e:
            print(f"⚠️ No se pudo adjuntar logo EcoFact: {e}")
        
        # Adjuntar logo Apple Pereira
        try:
            with open(logo_apple_path, 'rb') as img:
                logo_apple = MIMEImage(img.read())
                logo_apple.add_header('Content-ID', '<logo_apple>')
                logo_apple.add_header('Content-Disposition', 'inline', filename='logo_apple.png')
                msg.attach(logo_apple)
                print("✅ Logo Apple Pereira adjuntado")
        except Exception as e:
            print(f"⚠️ No se pudo adjuntar logo Apple: {e}")
        
        resultado = msg.send(fail_silently=False)
        print(f"✅ Email enviado exitosamente. Resultado: {resultado}")
        print(f"✅ Código de recuperación enviado a {email}: {codigo}\n")
        
        return JsonResponse({
            'status': 'ok',
            'message': 'Código enviado. Revisa tu correo electrónico.'
        })
        
    except Exception as e:
        print(f"❌ Error al enviar código: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'status': 'error',
            'message': 'Error al enviar el código. Inténtalo de nuevo.'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def verificar_codigo_recuperacion(request):
    """Verifica si el código ingresado es válido"""
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()
        codigo = data.get('codigo', '').strip()
        
        if not email or not codigo:
            return JsonResponse({'status': 'error', 'message': 'Datos incompletos'}, status=400)
        
        # Buscar el código más reciente para este email
        try:
            codigo_obj = CodigoRecuperacion.objects.filter(
                email=email,
                codigo=codigo
            ).order_by('-creado_en').first()
            
            if not codigo_obj:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Código incorrecto'
                }, status=400)
            
            if not codigo_obj.es_valido():
                return JsonResponse({
                    'status': 'error',
                    'message': 'Código expirado. Solicita uno nuevo.'
                }, status=400)
            
            # Código válido
            return JsonResponse({
                'status': 'ok',
                'message': 'Código verificado correctamente'
            })
            
        except Exception as e:
            print(f"Error verificando código: {e}")
            return JsonResponse({
                'status': 'error',
                'message': 'Error al verificar el código'
            }, status=500)
            
    except Exception as e:
        print(f"❌ Error general: {e}")
        return JsonResponse({
            'status': 'error',
            'message': 'Error al procesar la solicitud'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def restablecer_contrasena(request):
    """Restablece la contraseña del usuario después de verificar el código"""
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()
        codigo = data.get('codigo', '').strip()
        nueva_password = data.get('password', '')
        
        if not email or not codigo or not nueva_password:
            return JsonResponse({'status': 'error', 'message': 'Datos incompletos'}, status=400)
        
        # Verificar código nuevamente
        codigo_obj = CodigoRecuperacion.objects.filter(
            email=email,
            codigo=codigo
        ).order_by('-creado_en').first()
        
        if not codigo_obj or not codigo_obj.es_valido():
            return JsonResponse({
                'status': 'error',
                'message': 'Código inválido o expirado'
            }, status=400)
        
        # Actualizar contraseña
        try:
            usuario = Usuario.objects.get(correo_electronico_usuario=email)
            usuario.set_password(nueva_password)
            usuario.save()
            
            # Marcar código como usado
            codigo_obj.usado = True
            codigo_obj.save()
            
            print(f"✅ Contraseña restablecida para {email}")
            
            return JsonResponse({
                'status': 'ok',
                'message': 'Contraseña restablecida exitosamente'
            })
            
        except Usuario.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Usuario no encontrado'
            }, status=404)
            
    except Exception as e:
        print(f"❌ Error al restablecer contraseña: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'status': 'error',
            'message': 'Error al restablecer la contraseña'
        }, status=500)