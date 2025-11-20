from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Q
from functools import wraps
import json
from .forms import RegistroUsuarioForm
from .models import Usuario

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