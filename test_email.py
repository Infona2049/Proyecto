import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EcoFactProject.settings')
django.setup()

from django.core.mail import EmailMultiAlternatives
from django.conf import settings
import random

# Generar código de prueba
codigo = ''.join([str(random.randint(0, 9)) for _ in range(6)])

# Email de prueba
email_destino = input("Ingresa el email donde quieres recibir el código de prueba: ").strip()

html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; }}
        .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .code-box {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; text-align: center; margin: 30px 0; }}
        .code {{ font-size: 48px; font-weight: bold; letter-spacing: 10px; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1 style="color: #2563eb; text-align: center;">Prueba de Email - EcoFact</h1>
        <div class="code-box">
            <div style="font-size: 14px; margin-bottom: 10px;">Tu código de prueba es:</div>
            <div class="code">{codigo}</div>
        </div>
        <p>Este es un email de prueba del sistema de recuperación de contraseñas.</p>
    </div>
</body>
</html>
"""

text_content = f"Tu código de prueba es: {codigo}"

print("\n" + "="*60)
print("📧 PRUEBA DE ENVÍO DE EMAIL")
print("="*60)
print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print(f"EMAIL_HOST_PASSWORD: {'*' * len(settings.EMAIL_HOST_PASSWORD)}")
print(f"De: {settings.EMAIL_HOST_USER}")
print(f"Para: {email_destino}")
print(f"Código generado: {codigo}")
print("="*60)

try:
    print("\n📤 Enviando email...")
    
    msg = EmailMultiAlternatives(
        subject='Prueba de Email - EcoFact',
        body=text_content,
        from_email=settings.EMAIL_HOST_USER,
        to=[email_destino]
    )
    msg.attach_alternative(html_content, "text/html")
    
    resultado = msg.send(fail_silently=False)
    
    print(f"✅ Email enviado exitosamente!")
    print(f"✅ Resultado: {resultado}")
    print(f"\n🔍 Revisa tu bandeja de entrada (y SPAM) en: {email_destino}")
    print(f"📝 Código esperado: {codigo}")
    
except Exception as e:
    print(f"\n❌ ERROR AL ENVIAR EMAIL:")
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    
    print("\n💡 Posibles causas:")
    print("1. Contraseña de aplicación incorrecta")
    print("2. Gmail bloqueando el acceso")
    print("3. Verificación en dos pasos no configurada")
    print("4. Firewall o antivirus bloqueando la conexión")
