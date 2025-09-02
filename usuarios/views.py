from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.exceptions import ValidationError
from gestion_espacios_academicos.models import Espacio, EspacioCampus, Solicitud
from gestion_espacios_academicos.forms import SolicitudForm
from datetime import timedelta
import os

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
    espacios_carrera = Espacio.objects.filter(activo=True)
    espacios_campus = EspacioCampus.objects.all()
    context = {
        'espacios_carrera': espacios_carrera,
        'espacios_campus': espacios_campus,
    }
    return render(request, 'usuarios/listar_espacios.html', context)

@login_required
def enviar_solicitud(request):
    espacios_carrera = Espacio.objects.filter(activo=True)
    espacios_campus  = EspacioCampus.objects.all()

    if request.method == 'POST':
        nombre_evento      = request.POST.get('nombre_evento', '').strip()
        fecha_evento       = request.POST.get('fecha_evento')
        tipo_espacio       = request.POST.get('tipo_espacio')
        espacio_carrera    = request.POST.get('espacio_carrera')
        espacio_campus     = request.POST.get('espacio_campus')
        archivo_adjunto    = request.FILES.get('archivo_adjunto')

        errores = []
        if not nombre_evento: errores.append('Nombre obligatorio.')
        if not fecha_evento:  errores.append('Fecha obligatoria.')
        if not archivo_adjunto: errores.append('Archivo obligatorio.')
        if tipo_espacio == 'carrera' and not espacio_carrera: errores.append('Selecciona carrera.')
        if tipo_espacio == 'campus' and not espacio_campus:   errores.append('Selecciona campus.')

        if errores:
            for e in errores: messages.error(request, e)
        else:
            Solicitud.objects.create(
                usuario_solicitante=request.user,
                nombre_evento=nombre_evento,
                descripcion_evento=request.POST.get('descripcion_evento', ''),
                fecha_evento=fecha_evento,
                fecha_fin_evento=request.POST.get('fecha_fin_evento') or None,
                tipo_espacio=tipo_espacio,
                espacio_id=espacio_carrera if tipo_espacio == 'carrera' else None,
                espacio_campus_id=espacio_campus if tipo_espacio == 'campus' else None,
                archivo_adjunto=archivo_adjunto,
                estado='pendiente',
            )
            messages.success(request, '¡Solicitud enviada!')
            return redirect('usuarios:usuario')

    return render(request, 'usuarios/enviar_solicitud.html', {
        'espacios_carrera': espacios_carrera,
        'espacios_campus': espacios_campus,
    })