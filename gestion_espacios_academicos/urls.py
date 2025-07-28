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

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),  # Home page
    path('login/', views.login, name='login'),  # Login page
    path('logout/', views.logout, name='logout'),
    path('registro/', views.registro, name='registro'),  # Registration page
    path('dashboard_administrador/', include('administrador.urls')),  # Include admin URLs
    path('dashboard_encargados/', include('encargados.urls')),  # Include manager URLs
    path('reportes/', include('reportes.urls')),  # Include reports URLs
    path('usuarios/', include('usuarios.urls')),  # Include user management URLs
]
