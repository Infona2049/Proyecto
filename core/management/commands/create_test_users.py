from django.core.management.base import BaseCommand
from core.models import Usuario

class Command(BaseCommand):
    help = 'Crea usuarios de prueba para cada rol'

    def handle(self, *args, **options):
        # Usuario administrador
        if not Usuario.objects.filter(username='admin').exists():
            admin = Usuario.objects.create_user(
                username='admin',
                correo_electronico_usuario='admin@ecofact.com',
                password='admin123',
                nombre_usuario='Admin',
                apellido_usuario='Sistema',
                numero_documento_usuario='12345678',
                rol_usuario='admin'
            )
            self.stdout.write(
                self.style.SUCCESS(f'Usuario administrador creado: {admin.correo_electronico_usuario}')
            )

        # Usuario vendedor
        if not Usuario.objects.filter(username='vendedor').exists():
            vendedor = Usuario.objects.create_user(
                username='vendedor',
                correo_electronico_usuario='vendedor@ecofact.com',
                password='vendedor123',
                nombre_usuario='Juan',
                apellido_usuario='Vendedor',
                numero_documento_usuario='87654321',
                rol_usuario='vendedor'
            )
            self.stdout.write(
                self.style.SUCCESS(f'Usuario vendedor creado: {vendedor.correo_electronico_usuario}')
            )

        # Usuario cliente
        if not Usuario.objects.filter(username='cliente').exists():
            cliente = Usuario.objects.create_user(
                username='cliente',
                correo_electronico_usuario='cliente@ecofact.com',
                password='cliente123',
                nombre_usuario='María',
                apellido_usuario='Cliente',
                numero_documento_usuario='11223344',
                rol_usuario='cliente'
            )
            self.stdout.write(
                self.style.SUCCESS(f'Usuario cliente creado: {cliente.correo_electronico_usuario}')
            )

        self.stdout.write(
            self.style.SUCCESS('Usuarios de prueba creados exitosamente!')
        )
        self.stdout.write('Credenciales de acceso:')
        self.stdout.write('Admin: admin@ecofact.com / admin123')
        self.stdout.write('Vendedor: vendedor@ecofact.com / vendedor123') 
        self.stdout.write('Cliente: cliente@ecofact.com / cliente123')