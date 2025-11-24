from django import forms
from .models import Producto

class ProductoForm(forms.ModelForm):
    """
    Formulario basado en el modelo Producto para crear o editar productos.
    Incluye los campos principales del modelo que se desean mostrar en el formulario.
    """

    stock_actual_inventario = forms.IntegerField(
        label="Stock actual",
        min_value=1,
        initial=1,
        help_text="Cantidad inicial en inventario (debe ser mayor a 1)"
    )

    precio_producto = forms.DecimalField(
        label="Precio",
        min_value=0.01,
        decimal_places=2,
        max_digits=10,
        help_text="Precio del producto (debe ser mayor a 1)"
    )

    # Permitir que el usuario escriba cualquier color en el formulario.
    color_producto = forms.CharField(
        label="Color",
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Color (escriba el color)'
        })
    )

    def clean_precio_producto(self):
        precio = self.cleaned_data.get('precio_producto')
        if precio is not None and precio <= 1:
            raise forms.ValidationError("El precio debe ser mayor a 1.")
        return precio

    def clean_stock_actual_inventario(self):
        stock = self.cleaned_data.get('stock_actual_inventario')
        if stock is not None and stock < 1:
            raise forms.ValidationError("El stock actual debe ser igual o mayor a 1.")
        return stock

    class Meta:
        model = Producto
        fields = [
            'nombre_producto',
            'categoria_producto',
            'modelo_producto',
            'capacidad_producto',
            'color_producto',
            'precio_producto',
            'imagen_producto',
        ]
        widgets = {
            'nombre_producto': forms.TextInput(attrs={
                'placeholder': 'Nombre del producto',
                'pattern': '[A-Za-zÁÉÍÓÚáéíóúÑñ0-9 ]+',
                'title': 'Letras, números y espacios',
                'oninput': "this.value = this.value.replace(/[^A-Za-zÁÉÍÓÚáéíóúÑñ0-9 ]/g, '')"
            }),
            # 'color_producto' se gestiona por el campo del formulario sobrescrito
        }