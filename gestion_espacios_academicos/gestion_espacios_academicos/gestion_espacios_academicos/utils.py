from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import uuid
import pytz

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

"""
Funciones helper para timezone y fechas
"""

# Timezone de Bolivia
BOLIVIA_TZ = pytz.timezone('America/La_Paz')


def fecha_local(fecha_utc):
    """
    Convierte una fecha UTC a timezone local de Bolivia
    
    Args:
        fecha_utc: datetime object (puede ser naive o aware)
    
    Returns:
        datetime object en timezone de Bolivia
    """
    if fecha_utc is None:
        return None
    
    # Si la fecha no tiene timezone, asumirla como UTC
    if fecha_utc.tzinfo is None:
        fecha_utc = pytz.UTC.localize(fecha_utc)
    
    # Convertir a timezone de Bolivia
    return fecha_utc.astimezone(BOLIVIA_TZ)


def fecha_formateada(fecha, formato='%d/%m/%Y %H:%M'):
    """
    Formatea una fecha al timezone local
    
    Args:
        fecha: datetime object
        formato: string de formato de fecha (default: 'DD/MM/YYYY HH:MM')
    
    Returns:
        string con la fecha formateada
    """
    if fecha is None:
        return 'N/A'
    
    fecha_local_tz = fecha_local(fecha)
    return fecha_local_tz.strftime(formato)


def ahora_local():
    """
    Retorna la fecha/hora actual en timezone de Bolivia
    
    Returns:
        datetime object en timezone de Bolivia
    """
    return timezone.now().astimezone(BOLIVIA_TZ)


def convertir_a_utc(fecha_local_naive):
    """
    Convierte una fecha naive (sin timezone) asumiendo que está en timezone de Bolivia
    a UTC para guardar en la base de datos
    
    Args:
        fecha_local_naive: datetime object naive (sin timezone)
    
    Returns:
        datetime object en UTC
    """
    if fecha_local_naive is None:
        return None
    
    # Localizar la fecha en timezone de Bolivia
    fecha_bolivia = BOLIVIA_TZ.localize(fecha_local_naive)
    
    # Convertir a UTC
    return fecha_bolivia.astimezone(pytz.UTC)