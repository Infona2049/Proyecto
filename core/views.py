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
            usuario = Usuario.objects.get(email=email)
            print(f"✅ Usuario encontrado: {usuario.nombre_usuario} (ID: {usuario.id})")
        except Usuario.DoesNotExist:
            print(f"❌ Usuario NO encontrado con email: '{email}'")
            print("📋 Verificando todos los emails en la BD...")
            todos_emails = Usuario.objects.values_list('email', 'nombre_usuario')
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
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                h1 {{ color: #2563eb; margin: 0; }}
                .code-box {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; text-align: center; margin: 30px 0; }}
                .code {{ font-size: 48px; font-weight: bold; letter-spacing: 10px; margin: 10px 0; }}
                .info {{ color: #64748b; font-size: 14px; line-height: 1.6; }}
                .warning {{ background-color: #fef3c7; padding: 15px; border-radius: 8px; border-left: 4px solid #f59e0b; margin: 20px 0; color: #92400e; }}
                .footer {{ text-align: center; color: #94a3b8; font-size: 12px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e2e8f0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Recuperación de Contraseña</h1>
                </div>
                
                <p>Hola <strong>{usuario.nombre_usuario}</strong>,</p>
                
                <p class="info">
                    Recibimos una solicitud para restablecer la contraseña de tu cuenta en EcoFact.
                    Usa el siguiente código para continuar con el proceso:
                </p>
                
                <div class="code-box">
                    <div style="font-size: 14px; margin-bottom: 10px;">Tu código de verificación es:</div>
                    <div class="code">{codigo}</div>
                    <div style="font-size: 12px; margin-top: 10px;">Válido por 10 minutos</div>
                </div>
                
                <div class="warning">
                    <strong>⚠️ Importante:</strong><br>
                    • Este código expira en 10 minutos<br>
                    • No compartas este código con nadie<br>
                    • Si no solicitaste este cambio, ignora este correo
                </div>
                
                <p class="info">
                    Si tienes alguna pregunta o necesitas ayuda, no dudes en contactarnos.
                </p>
                
                <div class="footer">
                    <p><strong>EcoFact - Sistema de Facturación Electrónica</strong></p>
                    <p>Este es un correo automático, por favor no responder.</p>
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
        
        # Intentar con send_mail primero (más simple)
        try:
            print("📤 Intentando con send_mail (método simple)...")
            resultado_simple = send_mail(
                subject=subject,
                message=text_content,
                from_email=from_email,
                recipient_list=[email],
                fail_silently=False,
            )
            print(f"✅ send_mail resultado: {resultado_simple}")
        except Exception as e:
            print(f"❌ send_mail falló: {e}")
            import traceback
            traceback.print_exc()
        
        # Intentar con EmailMultiAlternatives (con HTML)
        print("📤 Intentando con EmailMultiAlternatives (con HTML)...")
        msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        msg.attach_alternative(html_content, "text/html")
        
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
            usuario = Usuario.objects.get(email=email)
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