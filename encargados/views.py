from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from gestion_espacios_academicos.models import Solicitud
from django.utils import timezone
from datetime import datetime
from django.core.mail import send_mail
import json
from django.db.models import Q
from usuarios.views import notificar_aceptacion_solicitud
from django.views.decorators.cache import never_cache

@login_required
@never_cache  # 🔥 CRÍTICO: No cachear
def dashboard_encargados(request):
    """
    Dashboard del encargado de espacios
    """
    user = request.user

    # 🔒 Verificar que sea encargado
    if user.tipo_usuario != 'encargado':
        messages.error(request, '⛔ No tienes permiso para acceder a esta página.')
        return redirect('login')
    
    # 🔍 Debug: Verificar sesión
    print(f"👔 Dashboard Encargado: {user.username} (ID: {user.id}, Rol: {user.tipo_usuario})")
    print(f"   Session Key: {request.session.session_key}")

    # ✅ Obtener solo los espacios que gestiona este encargado
    espacios_carrera = user.espacios_encargados.all()
    espacios_campus = user.espacios_campus_encargados.all()

    # ✅ Combinar ambos tipos de espacios
    espacios = list(espacios_carrera) + list(espacios_campus)

    # ✅ Si solo tiene uno, lo preseleccionamos
    espacio_preseleccionado = espacios[0] if len(espacios) == 1 else None

    context = {
        'mes_actual': timezone.now().strftime('%B %Y'),
        'espacios': espacios,
        'espacio_preseleccionado': espacio_preseleccionado,
        'usuario': user,  # ✅ Pasar usuario explícitamente
        'encargado': user,  # ✅ Alias para templates
        'session_key': request.session.session_key[:10],  # Para debugging
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
@require_POST
def cancelar_evento(request):
    user = request.user
    try:
        # 🔧 FIX: Obtener el ID correctamente (puede venir como JSON o POST)
        if request.content_type == 'application/json':
            import json
            data = json.loads(request.body)
            solicitud_id = data.get('solicitud_id')
            motivo = data.get('motivo', '')
        else:
            solicitud_id = request.POST.get('solicitud_id')
            motivo = request.POST.get('motivo', '')
        
        # Validar que tenemos el ID
        if not solicitud_id:
            return JsonResponse({
                'status': 'error',
                'message': 'No se proporcionó el ID de la solicitud.'
            }, status=400)
        
        solicitud = Solicitud.objects.get(id=solicitud_id)
        
        # Verificar permisos
        if user.tipo_usuario != 'encargado':
            return JsonResponse({
                'status': 'error',
                'message': 'No tienes permiso para realizar esta acción.'
            })
        
        es_encargado = (
            (solicitud.espacio and solicitud.espacio.encargado == user) or
            (solicitud.espacio_campus and solicitud.espacio_campus.encargado == user)
        )
        
        if not es_encargado:
            return JsonResponse({
                'status': 'error',
                'message': 'No eres encargado de este espacio.'
            })
        
        # Cancelar el evento
        solicitud.estado = 'cancelada'
        if motivo:
            solicitud.observaciones = f"Cancelado: {motivo}"
        else:
            solicitud.observaciones = "Cancelado por el encargado del espacio"
        solicitud.save()
        
        # 📧 ENVIAR CORREO DE NOTIFICACIÓN AL USUARIO
        enviar_correo_cancelacion(solicitud, motivo, user)
        
        return JsonResponse({
            'status': 'success',
            'message': 'Evento cancelado exitosamente. Se ha notificado al solicitante por correo.'
        })
        
    except Solicitud.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Solicitud no encontrada.'
        }, status=404)
    except Exception as e:
        print(f"❌ Error al cancelar: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'status': 'error',
            'message': f'Error al cancelar: {str(e)}'
        }, status=500)

def enviar_correo_cancelacion(solicitud, motivo, encargado):
    """
    Envía un correo HTML al solicitante notificando la cancelación del evento.
    """
    try:
        from django.core.mail import EmailMultiAlternatives
        from django.template.loader import render_to_string
        from django.utils import timezone as django_timezone
        import pytz
        
        user = solicitud.usuario_solicitante
        
        if not user.email:
            print(f"⚠️ El usuario {user.username} no tiene email configurado")
            return False
        
        # Preparar información
        nombre_solicitante = user.get_full_name() or user.username
        encargado_nombre = encargado.get_full_name() or encargado.username
        
        # ✅ CORRECCIÓN: Convertir a zona horaria de Bolivia antes de formatear
        bolivia_tz = pytz.timezone('America/La_Paz')
        fecha_evento_bolivia = solicitud.fecha_evento.astimezone(bolivia_tz)
        fecha_evento_str = fecha_evento_bolivia.strftime("%d/%m/%Y a las %H:%M")
        
        # ✅ CORRECCIÓN: Obtener el nombre CORRECTO del espacio
        if solicitud.tipo_espacio == 'carrera' and solicitud.espacio:
            espacio_nombre = solicitud.espacio.nombre  # Nombre del espacio, no de la carrera
            tipo_espacio_display = f"Espacio de Carrera - {solicitud.espacio.carrera.nombre}"
        elif solicitud.tipo_espacio == 'campus' and solicitud.espacio_campus:
            espacio_nombre = solicitud.espacio_campus.nombre
            tipo_espacio_display = "Espacio de Campus"
        else:
            espacio_nombre = "No especificado"
            tipo_espacio_display = "No especificado"
        
        motivo_texto = motivo if motivo else "No se especificó un motivo"
        
        # Preparar contexto para el template
        context = {
            'solicitud': solicitud,
            'user': user,
            'nombre_solicitante': nombre_solicitante,
            'nombre_evento': solicitud.nombre_evento,
            'fecha_evento': fecha_evento_str,
            'espacio_nombre': espacio_nombre,
            'tipo_espacio': tipo_espacio_display,
            'encargado_nombre': encargado_nombre,
            'motivo': motivo_texto,
        }
        
        # ✅ Renderizar HTML del correo
        html_message = render_to_string('encargados/confirmacion_cancelacion.html', context)
        
        # Crear correo
        subject = f"⚠️ Evento Cancelado - {solicitud.nombre_evento}"
        
        # Texto plano alternativo
        text_message = f"""
Estimado/a {nombre_solicitante},

Lamentamos informarte que tu evento ha sido CANCELADO por el encargado del espacio.

DETALLES DEL EVENTO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 Evento: {solicitud.nombre_evento}
📅 Fecha: {fecha_evento_str}
📍 Espacio: {espacio_nombre}
🏢 Tipo: {tipo_espacio_display}
👤 Cancelado por: {encargado_nombre}

MOTIVO DE LA CANCELACIÓN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{motivo_texto}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Si tienes alguna pregunta o necesitas más información, por favor contacta al encargado del espacio.

Puedes realizar una nueva solicitud en cualquier momento a través del sistema.

---
Sistema de Gestión de Espacios - UABJB
Universidad Autónoma del Beni José Ballivián
        """
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        
        email.attach_alternative(html_message, "text/html")
        email.send(fail_silently=False)
        
        print(f"✅ Correo de cancelación enviado a {user.email}")
        print(f"   Evento: {solicitud.nombre_evento}")
        print(f"   Espacio: {espacio_nombre}")
        print(f"   Fecha (Bolivia): {fecha_evento_str}")
        print(f"   Motivo: {motivo_texto}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al enviar correo de cancelación: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

@login_required
def aprobar_solicitud(request, solicitud_id):
    """
    Aprueba una solicitud verificando conflictos de horario
    """
    try:
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        
        # 🔍 VERIFICAR CONFLICTOS DE HORARIO (AHORA EXCLUYE ELIMINADAS)
        conflictos = verificar_conflictos_horario(solicitud)
        
        if conflictos:
            # Si hay conflictos, devolver información detallada
            conflictos_info = [{
                'nombre_evento': c.nombre_evento,
                'fecha': c.fecha_evento.strftime('%d/%m/%Y'),
                'hora': c.fecha_evento.strftime('%H:%M'),
                'solicitante': c.usuario_solicitante.get_full_name() or c.usuario_solicitante.username
            } for c in conflictos]
            
            return JsonResponse({
                'status': 'warning',
                'message': '⚠️ Hay conflictos de horario con otras reservas aceptadas.',
                'conflictos': conflictos_info
            })
        
        # 1️⃣ CAMBIAR ESTADO A ACEPTADA
        solicitud.estado = 'aceptada'
        solicitud.fecha_aprobacion = timezone.now()
        solicitud.save()
        
        # 2️⃣ 🔔 ENVIAR CORREO CON TOKEN Y QR
        print(f"📧 Enviando confirmación de aceptación para solicitud {solicitud_id}...")
        notificar_aceptacion_solicitud(solicitud, encargado=request.user)
        
        # 3️⃣ DEVOLVER JSON
        return JsonResponse({
            'status': 'success', 
            'message': '✅ Solicitud aprobada y notificación enviada al solicitante.'
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error', 
            'message': f'Error al aprobar la solicitud: {str(e)}'
        }, status=500)

def verificar_conflictos_horario(solicitud):
    """
    Verifica si hay conflictos de horario en el mismo espacio
    Retorna una lista de solicitudes que tienen conflicto
    SOLO considera solicitudes con estado 'aceptada' y NO eliminadas
    """
    from datetime import timedelta
    
    # ✅ Determinar inicio y fin del evento
    inicio = solicitud.fecha_evento
    
    # Si tiene fecha_fin_evento, usarla; sino asumir 2 horas
    if solicitud.fecha_fin_evento:
        fin = solicitud.fecha_fin_evento
    else:
        fin = solicitud.fecha_evento + timedelta(hours=2)
    
    # ✅ IMPORTANTE: Solo buscar solicitudes ACEPTADAS y NO ELIMINADAS
    query_base = Solicitud.objects.filter(
        estado='aceptada',  # ⭐ SOLO ACEPTADAS
        eliminada=False     # ⭐ NO ELIMINADAS
    ).exclude(
        id=solicitud.id     # Excluir la solicitud actual
    )
    
    # Filtrar por el mismo espacio
    if solicitud.tipo_espacio == 'carrera' and solicitud.espacio:
        query_base = query_base.filter(
            tipo_espacio='carrera',
            espacio=solicitud.espacio
        )
    elif solicitud.tipo_espacio == 'campus' and solicitud.espacio_campus:
        query_base = query_base.filter(
            tipo_espacio='campus',
            espacio_campus=solicitud.espacio_campus
        )
    else:
        return []  # Si no hay espacio definido, no hay conflictos
    
    # ✅ LÓGICA MEJORADA: Buscar conflictos de horario
    conflictos = []
    
    for otra_solicitud in query_base:
        # Determinar rango de la otra solicitud
        otro_inicio = otra_solicitud.fecha_evento
        
        if otra_solicitud.fecha_fin_evento:
            otro_fin = otra_solicitud.fecha_fin_evento
        else:
            otro_fin = otra_solicitud.fecha_evento + timedelta(hours=2)
        
        # ✅ VERIFICAR SI HAY SOLAPAMIENTO
        # Hay conflicto si:
        # - El nuevo evento empieza antes de que termine el otro
        # - Y el nuevo evento termina después de que empiece el otro
        if inicio < otro_fin and fin > otro_inicio:
            conflictos.append(otra_solicitud)
    
    for c in conflictos:
        c_fin = c.fecha_fin_evento or c.fecha_evento + timedelta(hours=2)
        print(f"      - {c.nombre_evento}")
        print(f"        Inicio: {c.fecha_evento} | Fin: {c_fin}")
        print(f"        Estado: {c.estado} | Eliminada: {c.eliminada}")
    
    return conflictos

@login_required
def aprobar_con_conflicto(request, solicitud_id):
    """
    Aprueba una solicitud ignorando los conflictos de horario
    (solo si el encargado confirma explícitamente)
    """
    try:
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        
        # Cambiar estado a aceptada
        solicitud.estado = 'aceptada'
        solicitud.fecha_aprobacion = timezone.now()
        solicitud.save()
        
        # Enviar correo con token y QR
        notificar_aceptacion_solicitud(solicitud, encargado=request.user)
        
        return JsonResponse({
            'status': 'success', 
            'message': '✅ Solicitud aprobada (conflicto ignorado) y notificación enviada.'
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
@require_POST
def eliminar_solicitud(request, solicitud_id):
    user = request.user
    
    try:
        solicitud = Solicitud.objects.get(id=solicitud_id)
        
        # Verificar permisos
        if user.tipo_usuario != 'encargado':
            return JsonResponse({
                'status': 'error',
                'message': 'No tienes permiso para realizar esta acción.'
            })
        
        es_encargado = (
            (solicitud.espacio and solicitud.espacio.encargado == user) or
            (solicitud.espacio_campus and solicitud.espacio_campus.encargado == user)
        )
        
        if not es_encargado:
            return JsonResponse({
                'status': 'error',
                'message': 'No eres encargado de este espacio.'
            })
        
        # ✅ MARCAR COMO ELIMINADA EN LUGAR DE BORRAR
        solicitud.eliminada = True
        solicitud.fecha_eliminacion = timezone.now()
        solicitud.estado = 'eliminada'  # Opcional: cambiar el estado
        solicitud.save()
        
        return JsonResponse({
            'status': 'success',
            'message': f'La solicitud fue eliminada exitosamente.'
        })
        
    except Solicitud.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Solicitud no encontrada.'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error al eliminar: {str(e)}'
        })

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
            'tipo_espacio': s.get_tipo_espacio_display(),
            'nombre_usuario': s.usuario_solicitante.get_full_name() or s.usuario_solicitante.username,
            'hora': s.fecha_evento.strftime('%H:%M'),
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

# Agregar esta función a tu views.py de encargados

@login_required
def crear_evento(request):

    print("✅ Usuario:", request.user)
    print("✅ Tipo:", request.user.tipo_usuario)
    print("✅ CSRF Token recibido:", request.headers.get('X-CSRFToken'))

    """
    Vista para que el encargado cree un evento/solicitud manualmente
    """
    user = request.user
    
    # Verificar que sea encargado
    if user.tipo_usuario != 'encargado':
        return JsonResponse({
            'status': 'error', 
            'message': 'No tienes permisos para crear eventos.'
        }, status=403)
    
    try:
        # Obtener datos del formulario
        nombre_evento = request.POST.get('nombre_evento', '').strip()
        nombre_solicitante = request.POST.get('nombre_solicitante', '').strip()
        fecha_evento = request.POST.get('fecha_evento')
        hora_evento = request.POST.get('hora_evento')
        espacio_id = request.POST.get('espacio_id')
        descripcion = request.POST.get('descripcion', '').strip()
        
        # Validaciones
        if not all([nombre_evento, nombre_solicitante, fecha_evento, hora_evento, espacio_id]):
            return JsonResponse({
                'status': 'error',
                'message': 'Todos los campos obligatorios deben ser completados.'
            }, status=400)
        
        # Determinar tipo de espacio y validar permisos
        espacio_carrera = None
        espacio_campus = None
        tipo_espacio = None
        
        # Buscar en espacios de carrera
        try:
            espacio_carrera = user.espacios_encargados.get(id=espacio_id)
            tipo_espacio = 'carrera'
        except:
            # Buscar en espacios de campus
            try:
                espacio_campus = user.espacios_campus_encargados.get(id=espacio_id)
                tipo_espacio = 'campus'
            except:
                return JsonResponse({
                    'status': 'error',
                    'message': 'El espacio seleccionado no existe o no tienes permisos para gestionarlo.'
                }, status=400)
        
        # Combinar fecha y hora
        fecha_hora_str = f"{fecha_evento} {hora_evento}"
        fecha_hora = datetime.strptime(fecha_hora_str, '%Y-%m-%d %H:%M')
        fecha_hora = timezone.make_aware(fecha_hora)  # ✅ Agrega esta línea

        if fecha_hora < timezone.now():
            return JsonResponse({
                'status': 'error',
                'message': 'No se puede crear un evento en el pasado.'
            }, status=400)
        
        # Crear la solicitud/evento
        solicitud = Solicitud.objects.create(
            # Usuario solicitante será el encargado que crea el evento
            usuario_solicitante=user,
            nombre_evento=nombre_evento,
            descripcion_evento=descripcion or f"Evento creado por {user.get_full_name() or user.username} para {nombre_solicitante}",
            fecha_evento=fecha_hora,
            tipo_espacio=tipo_espacio,
            espacio=espacio_carrera if tipo_espacio == 'carrera' else None,
            espacio_campus=espacio_campus if tipo_espacio == 'campus' else None,
            estado='aceptada',  
        )
        
        return JsonResponse({
            'status': 'success',
            'message': f'Evento "{nombre_evento}" creado exitosamente para {nombre_solicitante}.'
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error al crear el evento: {str(e)}'
        }, status=500)