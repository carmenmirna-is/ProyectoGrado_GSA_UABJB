from django.shortcuts import render

def dashboard_encargados(request):
    return render(request, 'encargados/dashboard_encargados.html')

def lista_solicitudes(request):
    return render(request, 'encargados/lista_solicitudes.html')

def solicitudes_pendientes(request):
    return render(request, 'encargados/solicitudes_pendientes.html')

def solicitudes_aceptadas(request):
    return render(request, 'encargados/solicitudes_aceptadas.html')

# Create your views here.