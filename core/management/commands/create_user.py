from django.core.management.base import BaseCommand
from core.models import Usuario

class Command(BaseCommand):
    help = 'Crea un usuario con el rol especificado'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Email del usuario', required=True)
        parser.add_argument('--password', type=str, help='Contraseña del usuario', required=True)
        parser.add_argument('--nombre', type=str, help='Nombre del usuario', required=True)
        parser.add_argument('--apellido', type=str, help='Apellido del usuario', required=True)
        parser.add_argument('--documento', type=str, help='Número de documento', required=True)
        parser.add_argument('--rol', type=str, choices=['admin', 'vendedor', 'cliente'], 
                          help='Rol del usuario (admin, vendedor, cliente)', required=True)
        parser.add_argument('--telefono', type=str, help='Teléfono (opcional)', required=False)

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        nombre = options['nombre']
        apellido = options['apellido']
        documento = options['documento']
        rol = options['rol']
        telefono = options.get('telefono', '')

        # Verificar si el usuario ya existe
        if Usuario.objects.filter(correo_electronico_usuario=email).exists():
            self.stdout.write(
                self.style.ERROR(f'Error: Ya existe un usuario con el email {email}')
            )
            return

        if Usuario.objects.filter(numero_documento_usuario=documento).exists():
            self.stdout.write(
                self.style.ERROR(f'Error: Ya existe un usuario con el documento {documento}')
            )
            return

        try:
            # Crear el usuario
            usuario = Usuario.objects.create_user(
                username=email,
                correo_electronico_usuario=email,
                password=password,
                nombre_usuario=nombre,
                apellido_usuario=apellido,
                numero_documento_usuario=documento,
                telefono_usuario=telefono,
                rol_usuario=rol
            )

            self.stdout.write(
                self.style.SUCCESS(f'Usuario {rol} creado exitosamente!')
            )
            self.stdout.write(f'Email: {email}')
            self.stdout.write(f'Nombre: {nombre} {apellido}')
            self.stdout.write(f'Rol: {rol}')
            self.stdout.write(f'Documento: {documento}')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error al crear usuario: {str(e)}')
            )