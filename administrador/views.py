from django.shortcuts import render

def dashboard_administrador(request):
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

# Create your views here.
