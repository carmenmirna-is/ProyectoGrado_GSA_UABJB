from django.urls import path
from . import views

app_name = 'administrador'

urlpatterns = [
    path('', views.dashboard_administrador, name='dashboard_administrador'),  # Ruta vacía
    path('registrar_encargados/', views.registrar_encargados, name='registrar_encargados'),
    path('registrar_espacios/', views.registrar_espacios, name='registrar_espacios'),
    path('registrar_facultad/', views.registrar_facultad, name='registrar_facultad'),
    path('lista_facultades/', views.lista_facultades, name='lista_facultades'),
    path('editar_facultad/', views.editar_facultad, name='editar_facultad'),
    path('registrar_carrera/', views.registrar_carrera, name='registrar_carrera'),
    path('editar_carrera/', views.editar_carrera, name='editar_carrera'),
    path('lista_carreras/', views.lista_carreras, name='lista_carreras'),   
    path('lista_encargados/', views.lista_encargados, name='lista_encargados'),
    path('lista_espacios/', views.lista_espacios, name='lista_espacios'),
    path('editar_encargado/', views.editar_encargado, name='editar_encargado'),
    path('editar_espacios/', views.editar_espacios, name='editar_ espacios'),
    path('registrar_espacio_campus/', views.registrar_espacio_campus, name='registrar_espacio_campus'),
]