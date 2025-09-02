from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from gestion_espacios_academicos.models import Solicitud, Espacio
from gestion_espacios_academicos.forms import SolicitudRechazoForm
from django.utils import timezone
from django.core.mail import send_mail
import json

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

def lista_solicitudes(request):
    # Obtener todas las solicitudes con sus relaciones
    solicitudes = Solicitud.objects.select_related('usuario_solicitante', 'espacio').all().order_by('-id')
    
    context = {
        'solicitudes': solicitudes,
    }
    return render(request, 'encargados/lista_solicitudes.html', context)

def solicitudes_pendientes(request):
    solicitudes = Solicitud.objects.filter(estado='pendiente').select_related('usuario_solicitante', 'espacio')
    context = {
        'solicitudes': solicitudes,
    }
    return render(request, 'encargados/solicitudes_pendientes.html', context)

def solicitudes_aceptadas(request):
    solicitudes = Solicitud.objects.filter(estado='aceptada').select_related('usuario_solicitante', 'espacio')
    context = {
        'solicitudes': solicitudes,
    }
    return render(request, 'encargados/solicitudes_aceptadas.html', context)

@require_http_methods(["POST"])
def aprobar_solicitud(request, solicitud_id):
    try:
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        solicitud.estado = 'aceptada'
        solicitud.fecha_aprobacion = timezone.now()  # Si tienes este campo
        solicitud.save()
        
        # Enviar notificación por correo
        try:
            subject = 'Solicitud Aceptada - UABJB'
            message = f'''Estimado/a {solicitud.usuario_solicitante.first_name or solicitud.usuario_solicitante.username},

Tu solicitud "{solicitud.nombre_evento}" ha sido aceptada.

Detalles:
- Fecha: {solicitud.fecha_evento.strftime("%d/%m/%Y %H:%M")}
- Espacio: {solicitud.get_nombre_espacio()}
- Tipo de espacio: {solicitud.get_tipo_espacio_display()}

Gracias por usar nuestro sistema.

Saludos,
Sistema de Gestión UABJB'''
            
            send_mail(
                subject,
                message,
                'cibanezsanguino@gmail.com',
                [solicitud.usuario_solicitante.email],
                fail_silently=True,  # Cambiado a True para evitar errores de email
            )
        except Exception as e:
            print(f'Error enviando correo: {str(e)}')  # Log del error
        
        # Siempre devolver JSON para requests AJAX
        return JsonResponse({
            'status': 'success', 
            'message': 'Solicitud aprobada con éxito.'
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error', 
            'message': f'Error al aprobar la solicitud: {str(e)}'
        }, status=500)

@require_http_methods(["POST"])
def rechazar_solicitud(request, solicitud_id):
    try:
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        
        # Obtener el motivo desde POST data
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            motivo = data.get('motivo_rechazo')
        else:
            motivo = request.POST.get('motivo_rechazo')
        
        if not motivo:
            return JsonResponse({
                'status': 'error', 
                'message': 'Debe proporcionar un motivo de rechazo.'
            }, status=400)
        
        solicitud.estado = 'rechazada'
        solicitud.motivo_rechazo = motivo
        solicitud.save()
        
        # Enviar notificación por correo
        try:
            subject = 'Solicitud Rechazada - UABJB'
            message = f'''Estimado/a {solicitud.usuario_solicitante.first_name or solicitud.usuario_solicitante.username},

Lamentablemente tu solicitud "{solicitud.nombre_evento}" ha sido rechazada.

Motivo del rechazo:
{motivo}

Detalles de la solicitud:
- Fecha solicitada: {solicitud.fecha_evento.strftime("%d/%m/%Y %H:%M")}
- Espacio solicitado: {solicitud.get_nombre_espacio()}
- Tipo de espacio: {solicitud.get_tipo_espacio_display()}

Si tienes dudas o deseas realizar una nueva solicitud, no dudes en contactarnos.

Saludos,
Sistema de Gestión UABJB'''
            
            send_mail(
                subject,
                message,
                'cibanezsanguino@gmail.com',
                [solicitud.usuario_solicitante.email],
                fail_silently=True,
            )
        except Exception as e:
            print(f'Error enviando correo: {str(e)}')
        
        return JsonResponse({
            'status': 'success', 
            'message': 'Solicitud rechazada con éxito.'
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error', 
            'message': f'Error al rechazar la solicitud: {str(e)}'
        }, status=500)

@require_http_methods(["POST"])
def eliminar_solicitud(request, solicitud_id):
    try:
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        nombre_evento = solicitud.nombre_evento
        solicitud.delete()
        
        return JsonResponse({
            'status': 'success', 
            'message': f'Solicitud "{nombre_evento}" eliminada con éxito.'
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error', 
            'message': f'Error al eliminar la solicitud: {str(e)}'
        }, status=500)

def detalle_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(Solicitud, id=solicitud_id)
    if request.method == 'POST':
        # Lógica para editar (puedes añadir un formulario si lo necesitas)
        messages.success(request, 'Solicitud actualizada con éxito.')
        return redirect('encargados:lista_solicitudes')
    context = {
        'solicitud': solicitud,
    }
    return render(request, 'encargados/detalle_solicitud.html', context)

def editar_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(Solicitud, id=solicitud_id)
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            nombre_evento = request.POST.get('nombre_evento')
            descripcion = request.POST.get('descripcion')
            fecha_evento = request.POST.get('fecha_evento')
            hora_inicio = request.POST.get('hora_inicio')
            hora_fin = request.POST.get('hora_fin')
            tipo_espacio = request.POST.get('tipo_espacio')
            espacio_id = request.POST.get('espacio')
            
            # Validaciones básicas
            if not all([nombre_evento, descripcion, fecha_evento, hora_inicio, hora_fin, tipo_espacio]):
                messages.error(request, 'Todos los campos son obligatorios.')
                return render(request, 'encargados/editar_solicitud.html', {'solicitud': solicitud})
            
            # Actualizar la solicitud
            solicitud.nombre_evento = nombre_evento
            solicitud.descripcion = descripcion
            solicitud.fecha_evento = f"{fecha_evento} {hora_inicio}"
            solicitud.hora_inicio = hora_inicio
            solicitud.hora_fin = hora_fin
            solicitud.tipo_espacio = tipo_espacio
            
            if espacio_id:
                espacio = get_object_or_404(Espacio, id=espacio_id)
                solicitud.espacio = espacio
            
            solicitud.save()
            
            messages.success(request, f'Solicitud "{nombre_evento}" actualizada con éxito.')
            return redirect('encargados:solicitudes_aceptadas')
            
        except Exception as e:
            messages.error(request, f'Error al actualizar la solicitud: {str(e)}')
    
    # Obtener espacios para el select
    espacios = Espacio.objects.all()
    
    context = {
        'solicitud': solicitud,
        'espacios': espacios,
    }
    return render(request, 'encargados/editar_solicitud.html', context)