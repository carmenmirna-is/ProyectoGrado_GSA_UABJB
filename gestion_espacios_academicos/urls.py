"""
URL configuration for gestion_espacios_academicos project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/', views.registro, name='registro'),
    path('administrador/', include('administrador.urls')),  # ← Cambio aquí
    path('encargados/', include('encargados.urls')),          # ← Y aquí
    path('reportes/', include('reportes.urls')),
    path('usuarios/', include('usuarios.urls')),
    path('registro/', views.registro, name='registro'),
    path('verificar/<str:token>/', views.verificar_cuenta, name='verificar_cuenta'),
    path('recuperar/', views.recuperar_contrasena, name='recuperar_contrasena'),
    path('restablecer/<str:token>/', views.restablecer_contrasena, name='restablecer_contrasena'),
    path('reenviar-verificacion/', views.reenviar_verificacion, name='reenviar_verificacion'),
]   + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)