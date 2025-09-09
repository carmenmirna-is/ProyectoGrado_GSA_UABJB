from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from gestion_espacios_academicos.models import Solicitud, Espacio
from django.utils import timezone
from django.core.mail import send_mail
import json
from django.db.models import Q

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

@login_required
def lista_solicitudes(request):
    user = request.user

    # Verificar que sea encargado
    if user.tipo_usuario != 'encargado':
        messages.error(request, 'No tienes permiso para ver esta página.')
        return render(request, 'encargados/lista_solicitudes.html', {'solicitudes': []})

    # Filtrar solicitudes que pertenecen a espacios gestionados por este encargado
    solicitudes = (
        Solicitud.objects
        .select_related('usuario_solicitante', 'espacio', 'espacio_campus')
        .filter(
            Q(espacio__encargado=user) |
            Q(espacio_campus__encargado=user)
        )
        .order_by('-fecha_creacion')
    )

    return render(request, 'encargados/lista_solicitudes.html', {'solicitudes': solicitudes})

@login_required
def solicitudes_pendientes(request):
    user = request.user
    if user.tipo_usuario != 'encargado':
        messages.error(request, 'No tienes permiso para ver esta página.')
        return render(request, 'encargados/solicitudes_pendientes.html', {'solicitudes': []})

    # Solo pendientes de sus espacios
    solicitudes = (
        Solicitud.objects
        .select_related('usuario_solicitante', 'espacio', 'espacio_campus')
        .filter(estado='pendiente')
        .filter(
            Q(espacio__encargado=user) |
            Q(espacio_campus__encargado=user)
        )
        .order_by('-fecha_creacion')
    )

    return render(request, 'encargados/solicitudes_pendientes.html', {'solicitudes': solicitudes})

@login_required
def solicitudes_aceptadas(request):
    user = request.user
    if user.tipo_usuario != 'encargado':
        messages.error(request, 'No tienes permiso para ver esta página.')
        return render(request, 'encargados/solicitudes_aceptadas.html', {'solicitudes': []})

    # Solo aceptadas de sus espacios
    solicitudes = (
        Solicitud.objects
        .select_related('usuario_solicitante', 'espacio', 'espacio_campus')
        .filter(estado='aceptada')
        .filter(
            Q(espacio__encargado=user) |
            Q(espacio_campus__encargado=user)
        )
        .order_by('-fecha_creacion')
    )

    return render(request, 'encargados/solicitudes_aceptadas.html', {'solicitudes': solicitudes})

@login_required
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

@login_required
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

@login_required
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

@login_required
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

@login_required
def descargar_archivo(request, solicitud_id):
    solicitud = get_object_or_404(Solicitud, id=solicitud_id)
    if not solicitud.archivo_adjunto:
        raise Http404("Sin archivo.")
    return HttpResponse(
        open(solicitud.archivo_adjunto.path, 'rb'),
        content_type='application/octet-stream',
        headers={'Content-Disposition': f'attachment; filename="{solicitud.archivo_adjunto.name}"'}
    )

@login_required
def solicitudes_aceptadas_json(request):
    user = request.user

    if not user.is_encargado:
        return JsonResponse([], safe=False)

    # IDs de espacios de carrera que gestiona
    ids_carrera = user.espacios_encargados.values_list('id', flat=True)

    # IDs de espacios de campus que gestiona
    ids_campus = user.espacios_campus_encargados.values_list('id', flat=True)

    # Filtrar solicitudes aceptadas de ambos tipos
    aceptadas = Solicitud.objects.filter(
        estado='aceptada'
    ).filter(
        Q(
            tipo_espacio='carrera',
            espacio_id__in=ids_carrera
        ) |
        Q(
            tipo_espacio='campus',
            espacio_campus_id__in=ids_campus
        )
    ).select_related('espacio', 'espacio_campus')

    data = []
    for s in aceptadas:
        espacio_nombre = s.get_nombre_espacio()
        data.append({
            'fecha': s.fecha_evento.strftime('%Y-%-m-%-d'),
            'nombre_evento': s.nombre_evento,
            'espacio__nombre': espacio_nombre,
        })
    return JsonResponse(data, safe=False)

@login_required
def perfil_encargado(request):
    """
    Vista para mostrar el perfil del encargado con su información personal
    """
    # Verificar que el usuario sea encargado
    if request.user.tipo_usuario != 'encargado':
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('encargados:dashboard_encargados')
    
    # Obtener los espacios que gestiona el encargado
    # Según tu modelo, estas son las relaciones correctas:
    espacios_carrera = request.user.espacios_encargados.all()  # Espacio -> encargado
    espacios_campus = request.user.espacios_campus_encargados.all()  # EspacioCampus -> encargado
    
    context = {
        'encargado': request.user,
        'espacios_carrera': espacios_carrera,
        'espacios_campus': espacios_campus,
    }
    return render(request, 'encargados/perfil_encargado.html', context)

from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime

@login_required
@require_http_methods(["POST"])
def editar_fecha_aceptada(request):
    user = request.user
    if user.tipo_usuario != 'encargado':
        return JsonResponse({'status': 'error', 'message': 'Sin permisos'}, status=403)

    solicitud_id = request.POST.get('solicitud_id')
    nueva_fecha = parse_datetime(request.POST.get('nueva_fecha'))

    if not nueva_fecha:
        return JsonResponse({'status': 'error', 'message': 'Fecha inválida'}, status=400)

    solicitud = get_object_or_404(
        Solicitud,
        id=solicitud_id,
        estado='aceptada',
        espacio__encargado=user
    )  # o espacio_campus__encargado=user si aplica

    fecha_anterior = solicitud.fecha_evento
    solicitud.fecha_evento = nueva_fecha
    solicitud.save()

    # Notificar por correo
    try:
        send_mail(
            'Cambio de fecha en solicitud aceptada - UABJB',
            f'''Hola {solicitud.usuario_solicitante.first_name or solicitud.usuario_solicitante.username},

La fecha de tu solicitud "{solicitud.nombre_evento}" ha sido modificada.

Nueva fecha: {nueva_fecha.strftime('%d/%m/%Y %H:%M')}
Fecha anterior: {fecha_anterior.strftime('%d/%m/%Y %H:%M')}

Espacio: {solicitud.get_nombre_espacio()}

Si tienes dudas responde a este correo.

Saludos,
Sistema UABJB''',
            'cibanezsanguino@gmail.com',
            [solicitud.usuario_solicitante.email],
            fail_silently=True
        )
    except Exception as e:
        pass  # ya logueas si quieres

    return JsonResponse({'status': 'success', 'message': 'Fecha actualizada y usuario notificado.'})