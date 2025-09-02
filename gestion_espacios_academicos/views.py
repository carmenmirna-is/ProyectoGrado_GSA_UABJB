from django.shortcuts import render, redirect
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import authenticate
from django.contrib import messages
from .forms import CustomRegistrationForm
from django.contrib.auth import authenticate, login as django_login

def index(request):
    return render(request, 'index.html')

def registro(request):
    if request.method == 'POST':
        form = CustomRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registro exitoso. Por favor, inicia sesión.')
            return redirect('login')
        else:
            messages.error(request, 'Error en el registro. Verifica los datos.')
    else:
        form = CustomRegistrationForm()
    return render(request, 'registro.html', {'form': form})

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            django_login(request, user)

            if user.tipo_usuario == 'administrador':
                return redirect('administrador:dashboard_administrador')
            elif user.tipo_usuario == 'encargado':
                return redirect('encargados:dashboard_encargados')
            else:  # 'usuario'
                return redirect('usuarios:usuario')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')

    return render(request, 'login.html')

def logout_view(request):
    auth_logout(request)
    messages.success(request, 'Sesión cerrada con éxito.')
    return redirect('login')