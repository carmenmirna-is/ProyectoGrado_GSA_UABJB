from django.shortcuts import render, redirect

def index(request):
    return render(request, 'index.html')

def registro(request):
    return render(request, 'registro.html')

def login(request):
    return render(request, 'login.html')

def logout(request):
    request.session.flush()  # Eliminar la sesión
    return redirect('login')

def usuario(request):
    return render(request, 'usuarios/usuario.html')

def enviar_solicitud(request):
    return render(request, 'usuarios/enviar_solicitud.html')

def listar_espacios(request):
    return render(request, 'usuarios/listar_espacios.html')

def generar_reportes(request):
    return render(request, 'reportes/generar_reportes.html')
