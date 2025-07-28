from django.shortcuts import render

def generar_reportes(request):
    return render(request, 'reportes/generar_reportes.html')

# Create your views here.
