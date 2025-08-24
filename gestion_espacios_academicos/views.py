from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import CustomAuthenticationForm, CustomRegistrationForm

def index(request):
    return render(request, 'index.html')

def registro(request):
    if request.method == 'POST':
        form = CustomRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.refresh_from_db()  # Cargar los campos personalizados
            user.save()
            messages.success(request, 'Registro exitoso. Por favor, inicia sesión.')
            return redirect('login')
        else:
            messages.error(request, 'Error en el registro. Por favor, verifica los datos.')
    else:
        form = CustomRegistrationForm()
    return render(request, 'registro.html', {'form': form})

def login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Inicio de sesión exitoso.')
                # Redirigir según el tipo de usuario
                if user.tipo_usuario == 'administrador':
                    return redirect('administrador:dashboard_administrador')
                elif user.tipo_usuario == 'encargado':
                    return redirect('encargado:dashboard_encargado')  # Ajusta la URL si tienes una vista para encargados
                else:  # usuario
                    return redirect('usuario:dashboard_usuario')  # Ajusta la URL si tienes una vista para usuarios
            else:
                messages.error(request, 'Usuario o contraseña incorrectos.')
        else:
            messages.error(request, 'Error en el formulario. Verifica los datos.')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout(request):
    logout(request)
    messages.success(request, 'Sesión cerrada con éxito.')
    return redirect('login')