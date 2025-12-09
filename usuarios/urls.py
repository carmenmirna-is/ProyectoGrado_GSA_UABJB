from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('', views.usuario, name='usuario'),  # User profile page
    path('enviar_solicitud/', views.enviar_solicitud, name='enviar_solicitud'),  # Send request page
    path('listar_espacios/', views.listar_espacios, name='listar_espacios'),  # List spaces page
    path('api/eventos-usuario/', views.eventos_usuario_json, name='eventos_usuario_json'),
    path('mi-perfil/', views.perfil_usuario, name='perfil_usuario'),
    path('cambiar-contrasena/', views.cambiar_contrasena, name='cambiar_contrasena'),
    path('historial/', views.historial_solicitudes, name='historial_solicitudes'),
    path('editar/<int:id>/', views.editar_solicitud, name='editar_solicitud'),
    path('cancelar/<int:id>/', views.cancelar_solicitud, name='cancelar_solicitud'),
    path('editar-perfil/', views.editar_perfil, name='editar_perfil'),
    path('verificar-conflictos/', views.verificar_conflictos_antes_enviar, name='verificar_conflictos'),
    path('api/documento-espacio/<int:espacio_id>/', views.obtener_documento_espacio, name='obtener_documento_espacio'),
]