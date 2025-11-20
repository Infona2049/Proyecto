from django.core.management.base import BaseCommand
from core.models import Usuario

class Command(BaseCommand):
    help = 'Crea un superusuario admin para acceder al panel de Django'

    def handle(self, *args, **options):
        email = 'superadmin@ecofact.com'
        password = 'superadmin123'
        
        if not Usuario.objects.filter(correo_electronico_usuario=email).exists():
            usuario = Usuario.objects.create_superuser(
                username=email,
                correo_electronico_usuario=email,
                password=password,
                nombre_usuario='Super',
                apellido_usuario='Admin',
                numero_documento_usuario='00000000',
                rol_usuario='admin'
            )
            
            self.stdout.write(
                self.style.SUCCESS('Superusuario creado exitosamente!')
            )
            self.stdout.write('Email: superadmin@ecofact.com')
            self.stdout.write('Password: superadmin123')
            self.stdout.write('Accede en: http://localhost:8001/admin/')
        else:
            self.stdout.write(
                self.style.WARNING('El superusuario ya existe')
            )