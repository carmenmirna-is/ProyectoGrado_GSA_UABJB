"""
Middleware para gestión de timezone
"""
from django.utils import timezone
import pytz


class TimezoneMiddleware:
    """
    Middleware que establece el timezone de Bolivia en cada request
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.tz = pytz.timezone('America/La_Paz')

    def __call__(self, request):
        # Activar timezone de Bolivia para este request
        timezone.activate(self.tz)
        
        response = self.get_response(request)
        
        # Desactivar timezone después del request
        timezone.deactivate()
        
        return response
    
"""
Middleware para debugging de sesiones
"""
import logging

logger = logging.getLogger(__name__)

class SessionDebugMiddleware:
    """
    Middleware para detectar problemas de sesiones mezcladas
    SOLO USAR EN DESARROLLO
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Antes de procesar la request
        if request.user.is_authenticated:
            session_key = request.session.session_key
            user_id = request.user.id
            username = request.user.username
            
            # Log de la sesión actual
            logger.info(f"🔑 Session Key: {session_key[:10]}... | User: {username} (ID: {user_id})")
            
            # Verificar si hay datos inconsistentes
            session_user_id = request.session.get('_auth_user_id')
            if session_user_id and int(session_user_id) != user_id:
                logger.error(f"⚠️ SESIÓN INCONSISTENTE! Session dice: {session_user_id}, Request.user es: {user_id}")

        response = self.get_response(request)
        
        # Después de procesar la request
        # Verificar si se cambió el usuario durante la request
        if request.user.is_authenticated:
            after_user_id = request.user.id
            after_username = request.user.username
            logger.info(f"✅ Response para: {after_username} (ID: {after_user_id})")

        return response


class TimezoneMiddleware:
    """
    Middleware existente para timezone
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        from django.utils import timezone
        from zoneinfo import ZoneInfo
        
        # Activar timezone de Bolivia
        timezone.activate(ZoneInfo('America/La_Paz'))
        
        response = self.get_response(request)
        return response