from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from administrador.views import user_type_required
from .models import Solicitud, Espacio
from gestion_espacios_academicos.forms import SolicitudRechazoForm
from django.utils import timezone

# Decorador para restringir acceso por tipo de usuario (asumido de administradores)
@user_type_required('encargado')
def dashboard_encargados(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        espacio = request.POST.get('espacio')
        color = request.POST.get('color')
        # Lógica para guardar evento (puede integrarse con un modelo Evento si lo creas)
        messages.success(request, f'Evento "{nombre}" agregado con éxito.')
        return redirect('encargados:dashboard_encargados')
    context = {
        'mes_actual': timezone.now().strftime('%B %Y'),
    }
    return render(request, 'encargados/dashboard_encargados.html', context)

@user_type_required('encargado')
def lista_solicitudes(request):
    solicitudes = Solicitud.objects.all()
    context = {
        'solicitudes': solicitudes,
    }
    return render(request, 'encargados/lista_solicitudes.html', context)

@user_type_required('encargado')
def solicitudes_pendientes(request):
    solicitudes = Solicitud.objects.filter(estado='pendiente')
    context = {
        'solicitudes': [(s.id, s.nombre_evento, s.fecha, s.usuario.username) for s in solicitudes],
    }
    return render(request, 'encargados/solicitudes_pendientes.html', context)

@user_type_required('encargado')
def solicitudes_aceptadas(request):
    solicitudes = Solicitud.objects.filter(estado='aceptada')
    context = {
        'solicitudes': [(s.id, s.nombre_evento, s.fecha, s.usuario.username) for s in solicitudes],
    }
    return render(request, 'encargados/solicitudes_aceptadas.html', context)

@user_type_required('encargado')
def aprobar_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(Solicitud, id=solicitud_id)
    if request.method == 'POST':
        solicitud.estado = 'aceptada'
        solicitud.save()
        messages.success(request, 'Solicitud aprobada con éxito.')
        return redirect('encargados:solicitudes_pendientes')
    return redirect('encargados:solicitudes_pendientes')

@user_type_required('encargado')
def rechazar_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(Solicitud, id=solicitud_id)
    if request.method == 'POST':
        form = SolicitudRechazoForm(request.POST, instance=solicitud)
        if form.is_valid():
            form.save()
            solicitud.estado = 'rechazada'
            solicitud.save()
            messages.success(request, 'Solicitud rechazada con éxito.')
            return redirect('encargados:solicitudes_pendientes')
        else:
            messages.error(request, 'Error al rechazar la solicitud. Proporciona un motivo.')
    else:
        form = SolicitudRechazoForm(instance=solicitud)
    context = {
        'form': form,
        'solicitud_id': solicitud_id,
        'solicitante': solicitud.usuario.username,
    }
    return render(request, 'encargados/lista_solicitudes.html', context)

@user_type_required('encargado')
def eliminar_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(Solicitud, id=solicitud_id)
    if request.method == 'POST':
        solicitud.delete()
        messages.success(request, 'Solicitud eliminada con éxito.')
        return redirect('encargados:lista_solicitudes')
    return redirect('encargados:lista_solicitudes')

# Vista pendiente (para editar detalle, asumida por la plantilla)
@user_type_required('encargado')
def detalle_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(Solicitud, id=solicitud_id)
    if request.method == 'POST':
        # Lógica para editar (puedes añadir un formulario si lo necesitas)
        messages.success(request, 'Solicitud actualizada con éxito.')
        return redirect('encargados:lista_solicitudes')
    context = {
        'solicitud': solicitud,
    }
    return render(request, 'encargados/lista_solicitudes.html', context)  # Ajusta a una plantilla específica si la creas