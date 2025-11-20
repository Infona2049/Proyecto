from django.contrib import admin
from django.urls import path, include  
from core import views
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

def redirect_to_login(request):
    return redirect('login')

urlpatterns = [
    path('', redirect_to_login, name='home'),  # Redirección de la ruta raíz al login
    path('admin/', admin.site.urls),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('vendedor-dashboard/', views.vendedor_dashboard_view, name='vendedor_dashboard'),
    path('cliente-dashboard/', views.cliente_dashboard_view, name='cliente_dashboard'),
    path('documentos/', views.documentos_view, name='documentos'),
    path('actualizar_perfil/', views.actualizar_perfil_view, name='actualizar_perfil'),
    path('cambiocontraseña/', views.cambiocontraseña_view, name='cambiocontraseña'),
    path('acerca_nosotros/', views.acerca_nosotros_view, name='acerca_nosotros'),
    path('productos/', include('productos.urls')),  
    path('historial_factura/', views.historial_factura_view, name='historial_factura'),
    path("facturas/", include("facturas.urls")),
    path('olvido_contraseña/', views.olvido_contraseña_view, name='olvido_contraseña'),
    path('registro/', views.registro_view, name='registro'),
    path('visualizacion_admin/', views.visualizacion_admin_view, name='visualizacion_admin'),
    path('visualizacion_cliente/', views.visualizacion_cliente_view, name='visualizacion_cliente'),
    path('visualizacion_vendedor/', views.visualizacion_vendedor_view, name='visualizacion_vendedor'),
    # Agrega aquí las demás rutas que necesites
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else settings.STATIC_ROOT)