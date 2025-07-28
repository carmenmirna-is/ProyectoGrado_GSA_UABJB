from django.urls import path
from . import views

app_name = 'administrador'

urlpatterns = [
    path('', views.dashboard_administrador, name='dashboard_administrador'),  # Ruta vacía
    path('registrar_encargados/', views.registrar_encargados, name='registrar_encargados'),
    path('registrar_espacios/', views.registrar_espacios, name='registrar_espacios'),
    path('lista_encargados/', views.lista_encargados, name='lista_encargados'),
    path('lista_espacios/', views.lista_espacios, name='lista_espacios'),
    path('editar_encargado/', views.editar_encargado, name='editar_encargado'),
    path('editar_espacios/', views.editar_espacios, name='editar_ espacios'),
]