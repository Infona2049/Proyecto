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
from .forms import RegistroUsuarioForm, PerfilForm
from .models import Usuario, CodigoRecuperacion
from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
import os
from django.template.loader import render_to_string
import traceback
from email.mime.image import MIMEImage



# Intento de usar premailer para inline CSS; si no está, usar identidad
try:
    from premailer import transform as premailer_transform
except Exception:
    def premailer_transform(s):
        return s


def _send_email_using_template(template_name, context, subject, to_email_list):
    """Renderiza una plantilla de email, aplica inline CSS y envía adjuntando logos como CID.
    Devuelve True si el envío parece correcto, False si hubo error.
    """
    try:
        html_content = render_to_string(template_name, context)
        html_inlined = premailer_transform(html_content)

        text_content = context.get('text_content') or f"Tu código es: {context.get('codigo','')}\nVálido por 10 minutos."

        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or getattr(settings, 'EMAIL_HOST_USER', 'no-reply@example.com')
        msg = EmailMultiAlternatives(subject, text_content, from_email, to_email_list)
        msg.attach_alternative(html_inlined, 'text/html')

        # Adjuntar logos como imágenes embebidas
        logo_ecofact_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'Logo azul sin fondo.png')
        logo_apple_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'logo empresa.png')

        try:
            with open(logo_ecofact_path, 'rb') as img:
                logo_ecofact = MIMEImage(img.read())
                logo_ecofact.add_header('Content-ID', '<logo_ecofact>')
                logo_ecofact.add_header('Content-Disposition', 'inline', filename='logo_ecofact.png')
                msg.attach(logo_ecofact)
        except Exception as e:
            print(f" No se pudo adjuntar logo EcoFact: {e}")

        try:
            with open(logo_apple_path, 'rb') as img:
                logo_apple = MIMEImage(img.read())
                logo_apple.add_header('Content-ID', '<logo_apple>')
                logo_apple.add_header('Content-Disposition', 'inline', filename='logo_apple.png')
                msg.attach(logo_apple)
        except Exception as e:
            print(f" No se pudo adjuntar logo Apple: {e}")

        resultado = msg.send(fail_silently=False)
        print(f"Email enviado a {to_email_list} (resultado: {resultado})")
        return True
    except Exception as e:
        print(f"Error enviando email desde plantilla: {e}")
        traceback.print_exc()
        return False


def _enviar_email_codigo_formateado(email, codigo, nombre_usuario=None):
    """Helper que construye el contexto y llama a la plantilla de email."""
    subject = 'Código de Validación - EcoFact'
    context = {
        'usuario_nombre': nombre_usuario or '',
        'codigo': codigo,
        'heading': ' Validación de Correo',
        'subtitle': 'Sistema de Seguridad EcoFact',
        'main_message': 'Hemos recibido una solicitud de creación de cuenta. Introduce el código a continuación para verificar tu correo y activar tu cuenta.',
        'code_label': 'Código de verificación:',
        'text_content': f"Tu código es: {codigo}\nVálido por 10 minutos."
    }
    return _send_email_using_template('core/emails/validacion_correo.html', context, subject, [email])

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
    """

    Esta vista permite que el usuario actual edite la información básica
    de su perfil: correo electrónico, dirección y teléfono.

    Contiene validaciones personalizadas altamente específicas:
    - Validación manual de formato del correo (debe contener "@")
    - Validación del teléfono (solo números, longitud entre 7 y 10)
    - Comparación individual campo por campo
    - Mensajería informativa si no hay cambios
    - Actualización del username si se modifica el correo
    - Evita duplicados en base de datos

    Además, la vista informa qué campos fueron modificados mediante mensajes
    dinámicos y vuelve a iniciar sesión al usuario para mantener su sesión activa
    tras cambiar las credenciales relacionadas.
    """

    user = request.user

    if request.method == 'POST':
        original_user = Usuario.objects.get(pk=user.pk)
        form = PerfilForm(request.POST, instance=user)

        if form.is_valid():
            cleaned = form.cleaned_data
            new_email = cleaned.get("correo_electronico_usuario", "").strip()
            new_direccion = cleaned.get("direccion_usuario", "").strip()
            new_telefono = cleaned.get("telefono_usuario", "").strip()

            cambios = []

            # VALIDACION CORREO
            if new_email and "@" not in new_email:
                messages.error(request, " El correo debe contener '@'.")
                return render(request, "core/actualizar_perfil.html", {"form": form})

            # VALIDACION TELÉFONO
            if new_telefono:
                if not new_telefono.isdigit():
                    messages.error(request, " El telefono solo debe contener numeros.")
                    return render(request, "core/actualizar_perfil.html", {"form": form})
                if len(new_telefono) < 7 or len(new_telefono) > 10:
                    messages.error(request, " El telefono debe tener entre 7 y 10 digitos.")
                    return render(request, "core/actualizar_perfil.html", {"form": form})

            # COMPARACION CAMPO A CAMPO
            if new_email.lower() != (original_user.correo_electronico_usuario or "").lower():
                if Usuario.objects.filter(correo_electronico_usuario=new_email).exclude(pk=user.pk).exists():
                    messages.error(request, " Este correo ya esta registrado.")
                    return redirect("actualizar_perfil")

                user.correo_electronico_usuario = new_email
                user.username = new_email
                cambios.append("correo electronico")

            if new_direccion != (original_user.direccion_usuario or ""):
                user.direccion_usuario = new_direccion
                cambios.append("direccion")

            if new_telefono != (original_user.telefono_usuario or ""):
                user.telefono_usuario = new_telefono
                cambios.append("telefono")

            # GUARDAR CAMBIOS
            if cambios:
                user.save()
                login(request, user)
                messages.success(request, f" Perfil actualizado correctamente ({', '.join(cambios)})")
            else:
                messages.info(request, " No realizaste ningun cambio.")

            return render(request, "core/actualizar_perfil.html", {"form": PerfilForm(instance=user)})

    else:
        form = PerfilForm(instance=user)

    return render(request, "core/actualizar_perfil.html", {"form": form})

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

def validacion_correo_view(request):
    """Renderiza la pantalla de validación de correo tras registro."""
    # Pasar contexto si hay un email en sesión (colocado por registro_view)
    auto_email = request.session.pop('auto_validation_email', None)
    return render(request, 'core/validacion_correo.html', {'auto_email': auto_email})

def registro_view(request):
    if request.method == 'POST':
        # Verificar si es una petición AJAX
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            try:
                # Guardar el usuario
                user = form.save()
                
                if is_ajax:
                    # Envío automático del código para peticiones AJAX también
                    try:
                        import random
                        codigo = ''.join([str(random.randint(0, 9)) for _ in range(6)])
                        email_destino = user.correo_electronico_usuario
                        CodigoRecuperacion.objects.create(email=email_destino, codigo=codigo)
                        # Enviar email con formato profesional (mismo template que olvido_contraseña)
                        try:
                            _enviar_email_codigo_formateado(email_destino, codigo, user.nombre_usuario)
                        except Exception as e:
                            print('Error enviando código formateado (AJAX):', e)

                        request.session['auto_validation_email'] = email_destino
                    except Exception as e:
                        print('Error enviando código automático (AJAX):', e)

                    # Responder con JSON para AJAX
                    return JsonResponse({
                        'success': True,
                        'message': 'Usuario registrado exitosamente. Ya puedes iniciar sesión.'
                    })
                else:
                    # Envío automático del código de verificación al correo recién registrado
                    try:
                        import random
                        codigo = ''.join([str(random.randint(0, 9)) for _ in range(6)])
                        email_destino = user.correo_electronico_usuario
                        # Guardar código en la base de datos
                        CodigoRecuperacion.objects.create(
                            email=email_destino,
                            codigo=codigo
                        )

                        # Enviar email con formato profesional (mismo template que olvido_contraseña)
                        try:
                            _enviar_email_codigo_formateado(email_destino, codigo, user.nombre_usuario)
                        except Exception as e:
                            print('Error enviando código formateado:', e)

                        # Guardar el email en sesión para que la página de validación lo use y arranque el temporizador
                        request.session['auto_validation_email'] = email_destino

                    except Exception as e:
                        # Si hay algún error en el envío, simplemente continuar y redirigir (no bloquear registro)
                        print('Error enviando código automático:', e)

                    messages.success(request, 'Usuario registrado exitosamente. Por favor valida tu correo.')
                    # Redirigir a la pantalla de validación
                    return redirect('validacion_correo')
                
            except Exception as e:
                if is_ajax:
                    return JsonResponse({
                        'success': False,
                        'message': f'Error al registrar usuario: {str(e)}'
                    })
                else:
                    messages.error(request, f'Error al registrar usuario: {str(e)}')
        else:
            # Si hay errores en el formulario
            if is_ajax:
                error_messages = []
                for field, errors in form.errors.items():
                    field_label = form.fields[field].label or field
                    for error in errors:
                        error_messages.append(f'{field_label}: {error}')
                return JsonResponse({
                    'success': False,
                    'message': '<br>'.join(error_messages)
                })
            else:
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
        
        print(f"\n DEBUG: Email recibido del frontend: '{email}'")
        
        if not email:
            print(" Email vacío")
            return JsonResponse({'status': 'error', 'message': 'El correo es obligatorio'}, status=400)
        
        # Verificar que el usuario existe
        try:
            usuario = Usuario.objects.get(correo_electronico_usuario=email)
            print(f" Usuario encontrado: {usuario.nombre_usuario} (PK: {usuario.pk})")
        except Usuario.DoesNotExist:
            print(f" Usuario NO encontrado con email: '{email}'")
            print(" Verificando todos los emails en la BD...")
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
        
        # Enviar correo con el código usando la plantilla
        print(f"\n INICIANDO ENVÍO DE EMAIL (plantilla)")
        print(f"Email destino: {email}")
        print(f"Código: {codigo}")
        print(f"Usuario encontrado: {usuario.nombre_usuario}")

        subject = 'Código de Recuperación - EcoFact'
        context = {
            'usuario_nombre': usuario.nombre_usuario,
            'codigo': codigo,
            'heading': ' Recuperación de Contraseña',
            'subtitle': 'Sistema de Seguridad EcoFact',
            'main_message': 'Recibimos una solicitud para restablecer la contraseña de tu cuenta en EcoFact. Usa el código único a continuación para continuar con la recuperación.',
            'code_label': 'Tu código de verificación es:',
            'text_content': f"Tu código de verificación es: {codigo}\nVálido por 10 minutos."
        }

        enviado = _send_email_using_template('core/emails/recuperacion_contrasena.html', context, subject, [email])

        if enviado:
            return JsonResponse({'status': 'ok', 'message': 'Código enviado. Revisa tu correo electrónico.'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Error al enviar el código. Inténtalo de nuevo.'}, status=500)
        
    except Exception as e:
        print(f" Error al enviar código: {e}")
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
        print(f" Error general: {e}")
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
            
            print(f" Contraseña restablecida para {email}")
            
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
        print(f" Error al restablecer contraseña: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'status': 'error',
            'message': 'Error al restablecer la contraseña'
        }, status=500)