from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Espacio, Solicitud
from gestion_espacios_academicos.forms import SolicitudForm
from datetime import timedelta

@login_required
def usuario(request):
    if request.method == 'POST':
        # Lógica para manejar interacciones del calendario (si se implementa en el futuro)
        pass
    context = {
        'mes_actual': timezone.now().strftime('%B %Y'),
    }
    return render(request, 'usuarios/usuario.html', context)

@login_required
def listar_espacios(request):
    espacios = Espacio.objects.all()
    context = {
        'espacios': espacios,
    }
    return render(request, 'usuarios/listar_espacios.html', context)

@login_required
def enviar_solicitud(request):
    if request.method == 'POST':
        form = SolicitudForm(request.POST, request.FILES)
        if form.is_valid():
            solicitud = form.save(commit=False)
            solicitud.usuario = request.user
            # Validar fecha (mínimo 3 días hábiles desde hoy)
            fecha_minima = timezone.now() + timedelta(days=3)
            if solicitud.fecha < fecha_minima:
                messages.error(request, 'La fecha debe ser al menos 3 días hábiles después de hoy.')
            else:
                solicitud.save()
                messages.success(request, 'Solicitud enviada con éxito. Espera la confirmación en 24-48 horas hábiles.')
                return redirect('usuarios:usuario')
        else:
            messages.error(request, 'Error en el formulario. Verifica los datos.')
    else:
        form = SolicitudForm()
    context = {
        'form': form,
    }
    return render(request, 'usuarios/enviar_solicitud.html', context)