from django.shortcuts import render, redirect
from gestion_espacios_academicos.models import Espacio, Encargado, Facultad, Carrera, Administrador

def dashboard_administrador(request):
    if not request.session.get('usuario_id') or request.session.get('tipo_usuario') != 'administrador':
        return redirect('login')

    return render(request, 'administrador/dashboard_administrador.html')
def registrar_encargados(request):
    return render(request, 'administrador/registrar_encargados.html')

def registrar_espacios(request):
    return render(request, 'administrador/registrar_espacios.html')

def lista_encargados(request):
    return render(request, 'administrador/lista_encargados.html')

def lista_espacios(request):
    return render(request, 'administrador/lista_espacios.html')

def editar_encargado(request):
    return render(request, 'administrador/editar_encargado.html')

def editar_espacios(request):
    return render(request, 'administrador/editar_espacios.html')

def registrar_facultad(request):
    return render(request, 'administrador/registrar_facultad.html')

def lista_facultades(request):
    return render(request, 'administrador/lista_facultades.html')

def editar_facultad(request):
    return render(request, 'administrador/editar_facultad.html')

def registrar_carrera(request):
    return render(request, 'administrador/registrar_carrera.html')  

def editar_carrera(request):
    return render(request, 'administrador/editar_carrera.html')

def lista_carreras(request):
    return render(request, 'administrador/lista_carreras.html')