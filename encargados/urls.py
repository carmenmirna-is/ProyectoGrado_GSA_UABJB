from django.urls import path
from . import views

app_name = 'encargados'

urlpatterns = [
    path('', views.dashboard_encargados, name='dashboard_encargados'),  # Dashboard for managers
    path('lista_solicitudes/', views.lista_solicitudes, name='lista_solicitudes'),  # List requests page
    path('solicitudes_pendientes/', views.solicitudes_pendientes, name='solicitudes_pendientes'),  # Pending requests page
    path('solicitudes_aceptadas/', views.solicitudes_aceptadas, name='solicitudes_aceptadas'),  # Accepted requests page
]