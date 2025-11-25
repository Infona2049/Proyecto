from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, TIPO_DOCUMENTO_CHOICES, ROL_USUARIO_CHOICES

class RegistroUsuarioForm(UserCreationForm):
    # Campos básicos
    nombre_usuario = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Primer nombre'
        })
    )
    
    segundo_nombre_usuario = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Segundo nombre (opcional)'
        })
    )
    
    apellido_usuario = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Primer apellido'
        })
    )
    
    segundo_apellido_usuario = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Segundo apellido (opcional)'
        })
    )
    
    # Documento
    tipo_documento_usuario = forms.ChoiceField(
        choices=TIPO_DOCUMENTO_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    numero_documento_usuario = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Número de documento'
        })
    )
    
    # Contacto
    correo_electronico_usuario = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com'
        })
    )
    
    direccion_usuario = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Dirección (opcional)'
        })
    )
    
    telefono_usuario = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Teléfono (opcional)'
        })
    )
    
    # Rol (por defecto cliente)
    rol_usuario = forms.ChoiceField(
        choices=[('cliente', 'Cliente')],  # Solo permitir registro como cliente
        initial='cliente',
        widget=forms.HiddenInput()  # Campo oculto
    )
    
    # Username automático basado en email
    username = forms.CharField(
        widget=forms.HiddenInput(),
        required=False
    )

    class Meta:
        model = Usuario
        fields = [
            'username',
            'nombre_usuario',
            'segundo_nombre_usuario', 
            'apellido_usuario',
            'segundo_apellido_usuario',
            'tipo_documento_usuario',
            'numero_documento_usuario',
            'correo_electronico_usuario',
            'direccion_usuario',
            'telefono_usuario',
            'rol_usuario',
            'password1',
            'password2'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar campos de contraseña
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control', 
            'placeholder': 'Confirmar contraseña'
        })

    def clean_correo_electronico_usuario(self):
        email = self.cleaned_data.get('correo_electronico_usuario')
        if Usuario.objects.filter(correo_electronico_usuario=email).exists():
            raise forms.ValidationError('Este correo electrónico ya está registrado.')
        return email

    def clean_numero_documento_usuario(self):
        documento = self.cleaned_data.get('numero_documento_usuario')
        if Usuario.objects.filter(numero_documento_usuario=documento).exists():
            raise forms.ValidationError('Este número de documento ya está registrado.')
        return documento

    def clean_password1(self):
        import re
        password = self.cleaned_data.get('password1')
        
        # Validar longitud mínima
        if len(password) < 8:
            raise forms.ValidationError('La contraseña debe tener al menos 8 caracteres.')
        
        # Validar que contenga al menos una letra mayúscula
        if not re.search(r'[A-Z]', password):
            raise forms.ValidationError('La contraseña debe contener al menos una letra mayúscula.')
        
        # Validar que contenga al menos una letra minúscula
        if not re.search(r'[a-z]', password):
            raise forms.ValidationError('La contraseña debe contener al menos una letra minúscula.')
        
        # Validar que contenga al menos un número
        if not re.search(r'\d', password):
            raise forms.ValidationError('La contraseña debe contener al menos un número.')
        
        # Validar que contenga al menos un carácter especial
        if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/;`~]', password):
            raise forms.ValidationError('La contraseña debe contener al menos un carácter especial (!@#$%^&*(),.?":{}|<>_-+=[]\\\/;`~).')
        
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        # Usar el email como username
        user.username = self.cleaned_data['correo_electronico_usuario']
        # Asignar rol de cliente por defecto
        user.rol_usuario = 'cliente'
        
        if commit:
            user.save()
        return user


class PerfilForm(forms.ModelForm):
    """
    Formulario creado para permitir que el usuario actualice:
    - Correo electrónico
    - Dirección
    - Teléfono

    Este formulario no permite modificar nombres, apellidos,
    documento ni rol (por seguridad del sistema).

    Es usado por la vista actualizar_perfil_view que contiene
    la lógica de validaciones personalizadas implementadas por Sebastián.
    """

    class Meta:
        model = Usuario
        fields = [
            "correo_electronico_usuario",
            "direccion_usuario",
            "telefono_usuario",
        ]
        widgets = {
            "correo_electronico_usuario": forms.EmailInput(attrs={"class": "form-control"}),
            "direccion_usuario": forms.TextInput(attrs={"class": "form-control"}),
            "telefono_usuario": forms.TextInput(attrs={"class": "form-control"}),
        }
