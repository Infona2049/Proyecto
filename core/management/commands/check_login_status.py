from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Command(BaseCommand):
    help = 'Muestra información sobre intentos de login y usuarios bloqueados'

    def add_arguments(self, parser):
        parser.add_argument(
            '--blocked-only', 
            action='store_true', 
            help='Mostrar solo usuarios bloqueados'
        )

    def handle(self, *args, **options):
        now = timezone.now()
        
        if options['blocked_only']:
            usuarios = User.objects.filter(
                bloqueado_hasta__isnull=False,
                bloqueado_hasta__gt=now
            )
            self.stdout.write(
                self.style.WARNING('=== USUARIOS BLOQUEADOS ===')
            )
        else:
            usuarios = User.objects.filter(
                intentos_fallidos__gt=0
            )
            self.stdout.write(
                self.style.WARNING('=== USUARIOS CON INTENTOS FALLIDOS ===')
            )

        if not usuarios.exists():
            self.stdout.write('No hay usuarios que coincidan con los criterios.')
            return

        for usuario in usuarios:
            estado = "🔒 BLOQUEADO" if usuario.esta_bloqueado() else "⚠️  CON INTENTOS"
            
            info = f"""
{estado} - {usuario.correo_electronico_usuario}
  - ID: {usuario.id_usuario}
  - Rol: {usuario.rol_usuario}
  - Intentos fallidos: {usuario.intentos_fallidos}
  - Último intento: {usuario.ultimo_intento_fallido or 'N/A'}
  - Bloqueado hasta: {usuario.bloqueado_hasta or 'N/A'}
"""
            
            if usuario.esta_bloqueado():
                tiempo_restante = usuario.bloqueado_hasta - now
                minutos_restantes = int(tiempo_restante.total_seconds() / 60)
                info += f"  - Tiempo restante: {minutos_restantes} minutos\n"
            
            self.stdout.write(info)

        # Estadísticas generales
        total_bloqueados = User.objects.filter(
            bloqueado_hasta__isnull=False,
            bloqueado_hasta__gt=now
        ).count()
        
        total_con_intentos = User.objects.filter(
            intentos_fallidos__gt=0
        ).count()

        self.stdout.write(
            self.style.SUCCESS(f"""
=== ESTADÍSTICAS ===
Total usuarios con intentos fallidos: {total_con_intentos}
Total usuarios bloqueados: {total_bloqueados}
""")
        )