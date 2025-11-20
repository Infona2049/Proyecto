from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Command(BaseCommand):
    help = 'Desbloquea un usuario por email o ID'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email', 
            type=str, 
            help='Email del usuario a desbloquear'
        )
        parser.add_argument(
            '--id', 
            type=int, 
            help='ID del usuario a desbloquear'
        )
        parser.add_argument(
            '--all', 
            action='store_true', 
            help='Desbloquear todos los usuarios bloqueados'
        )

    def handle(self, *args, **options):
        if options['all']:
            # Desbloquear todos los usuarios
            usuarios_bloqueados = User.objects.filter(
                bloqueado_hasta__isnull=False,
                bloqueado_hasta__gt=timezone.now()
            )
            count = usuarios_bloqueados.count()
            usuarios_bloqueados.update(
                intentos_fallidos=0,
                bloqueado_hasta=None,
                ultimo_intento_fallido=None
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Se desbloquearon {count} usuarios.'
                )
            )
            return

        # Buscar usuario específico
        usuario = None
        if options['email']:
            try:
                usuario = User.objects.get(correo_electronico_usuario=options['email'])
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(
                        f'No se encontró usuario con email: {options["email"]}'
                    )
                )
                return
        elif options['id']:
            try:
                usuario = User.objects.get(id_usuario=options['id'])
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(
                        f'No se encontró usuario con ID: {options["id"]}'
                    )
                )
                return
        else:
            self.stdout.write(
                self.style.ERROR(
                    'Debes proporcionar --email, --id o --all'
                )
            )
            return

        # Desbloquear usuario
        if usuario.esta_bloqueado():
            usuario.resetear_intentos_fallidos()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Usuario {usuario.correo_electronico_usuario} desbloqueado exitosamente.'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f'El usuario {usuario.correo_electronico_usuario} no estaba bloqueado.'
                )
            )