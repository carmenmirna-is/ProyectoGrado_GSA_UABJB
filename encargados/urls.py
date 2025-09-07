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
    path('eliminar_solicitud/<int:solicitud_id>/', views.eliminar_solicitud, name='eliminar_solicitud'),
    path('detalle_solicitud/<int:solicitud_id>/', views.detalle_solicitud, name='detalle_solicitud'),
    path('api/solicitudes-aceptadas/', views.solicitudes_aceptadas_json, name='solicitudes_aceptadas_json'),
    path('descargar/<int:solicitud_id>/', views.descargar_archivo, name='descargar_archivo'),
    path('perfil/', views.perfil_encargado, name='perfil_encargado'),
] 