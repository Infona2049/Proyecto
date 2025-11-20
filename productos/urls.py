
from django.urls import path
from . import views

urlpatterns = [
    # Ruta para la vista que muestra el inventario de productos
    path('inventario/', views.inventario_view, name='inventario'),

    # Ruta para la vista que permite registrar un nuevo producto
    path('registro_producto/', views.registro_producto_view, name='registro_producto'),

    # Rutas para editar y eliminar inventario
    path('inventario/<int:pk>/editar/', views.editar_inventario_view, name='editar_inventario'),
    path('inventario/<int:pk>/eliminar/', views.eliminar_inventario_view, name='eliminar_inventario'),

    #Ruta para buscar el producto en inventario 13/11/2025
    path("buscar/", views.buscar_producto, name="buscar_producto"),
]
