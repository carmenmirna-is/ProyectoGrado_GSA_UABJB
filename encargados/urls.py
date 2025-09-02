# encargados/urls.py
from django.urls import path
from . import views

app_name = 'encargados'

urlpatterns = [
    path('dashboard/', views.dashboard_encargados, name='dashboard_encargados'),
    path('lista_solicitudes/', views.lista_solicitudes, name='lista_solicitudes'),
    path('solicitudes_pendientes/', views.solicitudes_pendientes, name='solicitudes_pendientes'),
    path('solicitudes_aceptadas/', views.solicitudes_aceptadas, name='solicitudes_aceptadas'),
    path('aprobar_solicitud/<int:solicitud_id>/', views.aprobar_solicitud, name='aprobar_solicitud'),
    path('rechazar_solicitud/<int:solicitud_id>/', views.rechazar_solicitud, name='rechazar_solicitud'),
    path('editar_solicitud/<int:solicitud_id>/', views.editar_solicitud, name='editar_solicitud'),  # ← NUEVA LÍNEA
    path('eliminar_solicitud/<int:solicitud_id>/', views.eliminar_solicitud, name='eliminar_solicitud'),
    path('detalle_solicitud/<int:solicitud_id>/', views.detalle_solicitud, name='detalle_solicitud'),
] 