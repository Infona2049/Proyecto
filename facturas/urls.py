from django.urls import path # importa la función path para definir rutas
from . import views # importa las vistas del módulo actual

urlpatterns = [ # define las rutas para la aplicación de facturas
    path("crear/", views.crear_factura, name="crear_factura"),
    path("exitosa/", views.factura_exitosa, name="factura_exitosa"),
    path("historial_factura/", views.historial_factura, name="historial_factura"), 

    # rutas para ver, editar y eliminar facturas
    path("<int:pk>/print/", views.factura_print, name="factura_print"),
    path("<int:pk>/pdf/", views.factura_pdf, name="factura_pdf"),
    path("<int:pk>/xml/", views.factura_xml, name="factura_xml"),

    # ruta para buscar productos
    path('buscar_producto/', views.buscar_producto, name='buscar_producto'),
]