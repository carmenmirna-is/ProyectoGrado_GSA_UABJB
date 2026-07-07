from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import authenticate
from django.contrib import messages
from .forms import CustomRegistrationForm
from django.contrib.auth import authenticate, login as django_login
from django.utils import timezone
from .utils import enviar_correo_verificacion, enviar_correo_recuperacion
from django.contrib.auth import get_user_model

User = get_user_model()

def index(request):
    return render(request, 'index.html')

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

def registro(request):
    if request.method == 'POST':
        form = CustomRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # No puede iniciar sesión hasta verificar
            user.save()
            enviar_correo_verificacion(user, request)
            messages.success(request, 'Registro exitoso. Revisa tu correo para verificar tu cuenta.')
            return redirect('login')
        else:
            messages.error(request, 'Error en el registro. Verifica los datos.')
    else:
        form = CustomRegistrationForm()

    
    return render(request, 'registro.html', {'form': form})

def verificar_cuenta(request, token):
    user = get_object_or_404(User, token_verificacion=token)
    if user.token_expira and timezone.now() > user.token_expira:
        messages.error(request, 'El enlace ha expirado. Solicita uno nuevo.')
        return redirect('login')
    user.verificado = True
    user.is_active = True
    user.token_verificacion = None
    user.token_expira = None
    user.save()
    messages.success(request, 'Cuenta verificada. Ahora puedes iniciar sesión.')
    return redirect('login')

def recuperar_contrasena(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            enviar_correo_recuperacion(user, request)
            messages.success(request, 'Se ha enviado un enlace a tu correo.')
        except User.DoesNotExist:
            messages.error(request, 'No existe una cuenta con ese correo.')
    return render(request, 'recuperar_contrasena.html')

def restablecer_contrasena(request, token):
    user = get_object_or_404(User, token_verificacion=token)
    if user.token_expira and timezone.now() > user.token_expira:
        messages.error(request, 'El enlace ha expirado.')
        return redirect('login')
    if request.method == 'POST':
        nueva = request.POST.get('password')
        user.set_password(nueva)
        user.token_verificacion = None
        user.token_expira = None
        user.save()
        messages.success(request, 'Contraseña restablecida. Ahora puedes iniciar sesión.')
        return redirect('login')
    return render(request, 'restablecer_contrasena.html', {'token': token})

def reenviar_verificacion(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            if user.verificado:
                messages.warning(request, 'Esta cuenta ya está verificada.')
                return redirect('login')
            enviar_correo_verificacion(user, request)
            messages.success(request, 'Se ha reenviado el enlace de verificación.')
            return redirect('login')
        except User.DoesNotExist:
            messages.error(request, 'No existe una cuenta con ese correo.')
    return render(request, 'reenviar_verificacion.html')