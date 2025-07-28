from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('', views.usuario, name='usuario'),  # User profile page
    path('enviar_solicitud/', views.enviar_solicitud, name='enviar_solicitud'),  # Send request page
    path('listar_espacios/', views.listar_espacios, name='listar_espacios'),  # List spaces page
]