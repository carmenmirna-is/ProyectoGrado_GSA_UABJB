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

