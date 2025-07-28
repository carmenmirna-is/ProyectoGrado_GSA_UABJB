from django.shortcuts import render

def usuario(request):
    return render(request, 'usuarios/usuario.html')

def enviar_solicitud(request):
    return render(request, 'usuarios/enviar_solicitud.html')

def listar_espacios(request):
    return render(request, 'usuarios/listar_espacios.html')

# Create your views here.
