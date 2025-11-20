from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

class RoleRedirectMiddleware:
    """
    Middleware que redirige automáticamente a los usuarios autenticados
    a su dashboard correspondiente si intentan acceder a rutas de otros roles
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Definir las rutas y roles permitidos
        self.role_routes = {
            # Rutas de admin
            'admin_dashboard': ['admin'],
            'visualizacion_admin': ['admin'],
            
            # Rutas de vendedor
            'vendedor_dashboard': ['vendedor'],
            'visualizacion_vendedor': ['vendedor'],
            
            # Rutas de cliente
            'cliente_dashboard': ['cliente'],
            'visualizacion_cliente': ['cliente'],
        }
        
        # Dashboards por rol
        self.dashboards = {
            'admin': 'admin_dashboard',
            'vendedor': 'vendedor_dashboard',
            'cliente': 'cliente_dashboard'
        }

    def __call__(self, request):
        # Procesar la solicitud antes de la vista
        response = self.process_request(request)
        if response:
            return response
            
        # Continuar con el procesamiento normal
        response = self.get_response(request)
        return response

    def process_request(self, request):
        # Solo aplicar a usuarios autenticados
        if not request.user.is_authenticated:
            return None
            
        # Obtener el nombre de la vista actual
        current_view = None
        try:
            from django.urls import resolve
            current_view = resolve(request.path_info).url_name
        except:
            return None
            
        # Verificar si la vista actual requiere un rol específico
        if current_view in self.role_routes:
            allowed_roles = self.role_routes[current_view]
            user_role = getattr(request.user, 'rol_usuario', None)
            
            # Si el usuario no tiene el rol correcto, redirigir
            if user_role not in allowed_roles:
                messages.warning(
                    request, 
                    f'No tienes permisos para acceder a esa sección. Has sido redirigido a tu panel.'
                )
                
                # Redirigir al dashboard correspondiente
                if user_role in self.dashboards:
                    return redirect(self.dashboards[user_role])
                else:
                    return redirect('login')
        
        return None