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