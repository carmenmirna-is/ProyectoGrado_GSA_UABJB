from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import uuid

def generar_token():
    return str(uuid.uuid4())

def enviar_correo_verificacion(user, request):
    token = generar_token()
    user.token_verificacion = token
    user.token_expira = timezone.now() + timedelta(hours=24)
    user.save()

    protocol = 'https' if request.is_secure() else 'http'
    domain = request.get_host()  # ← localhost:8000 o abcd1234.ngrok-free.app
    enlace = f"{protocol}://{domain}/verificar/{token}/"

    asunto = "Verifica tu cuenta - Sistema UABJB"
    mensaje = f"""
    Hola {user.first_name},

    Gracias por registrarte. Haz clic en el enlace para verificar tu cuenta:

    {enlace}

    Este enlace expira en 24 horas.
    """
    send_mail(asunto, mensaje, settings.EMAIL_HOST_USER, [user.email])

def enviar_correo_recuperacion(user, request):
    token = generar_token()
    user.token_verificacion = token
    user.token_expira = timezone.now() + timedelta(hours=1)
    user.save()

    protocol = 'https' if request.is_secure() else 'http'
    domain = request.get_host()
    enlace = f"{protocol}://{domain}/restablecer/{token}/"

    asunto = "Restablece tu contraseña - Sistema UABJB"
    mensaje = f"""
    Hola {user.first_name},

    Haz clic en el enlace para restablecer tu contraseña:

    {enlace}

    Este enlace expira en 1 hora.
    """
    send_mail(asunto, mensaje, settings.EMAIL_HOST_USER, [user.email])