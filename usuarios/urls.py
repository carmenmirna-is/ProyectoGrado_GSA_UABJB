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
]