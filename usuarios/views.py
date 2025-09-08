from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from gestion_espacios_academicos.models import Espacio, EspacioCampus, Solicitud
from django.http import JsonResponse
from django.db.models import Q
from django.core.mail import send_mail  # 👈 NUEVA IMPORTACIÓN

def notificar_nueva_solicitud(solicitud):
    """
    Envía notificación por correo al encargado cuando llega una nueva solicitud
    """
    try:
        # Determinar el encargado según el tipo de espacio
        encargado = None
        
        if solicitud.tipo_espacio == 'carrera' and solicitud.espacio:
            encargado = solicitud.espacio.encargado
        elif solicitud.tipo_espacio == 'campus' and solicitud.espacio_campus:
            encargado = solicitud.espacio_campus.encargado
        
        # Si no hay encargado asignado o no tiene email, no enviar correo
        if not encargado:
            print(f'⚠️  No hay encargado asignado para el espacio de la solicitud: {solicitud.nombre_evento}')
            return
            
        if not encargado.email:
            print(f'⚠️  El encargado {encargado.username} no tiene email configurado')
            return
        
        # Preparar información del solicitante
        solicitante_nombre = f"{solicitud.usuario_solicitante.first_name} {solicitud.usuario_solicitante.last_name}".strip()
        if not solicitante_nombre:
            solicitante_nombre = solicitud.usuario_solicitante.username
        
        # Información académica del solicitante
        info_academica = ""
        if solicitud.usuario_solicitante.carrera:
            info_academica += f"- Carrera: {solicitud.usuario_solicitante.carrera}\n"
        if solicitud.usuario_solicitante.facultad:
            info_academica += f"- Facultad: {solicitud.usuario_solicitante.facultad}\n"
        
        # Preparar fechas de forma segura
        try:
            fecha_evento_str = solicitud.fecha_evento.strftime("%d/%m/%Y a las %H:%M")
        except:
            fecha_evento_str = str(solicitud.fecha_evento)
        
        try:
            fecha_creacion_str = solicitud.fecha_creacion.strftime("%d/%m/%Y a las %H:%M")
        except:
            fecha_creacion_str = str(solicitud.fecha_creacion)
        
        # Preparar el contenido del correo
        subject = '🔔 Nueva Solicitud Recibida - Sistema UABJB'
        
        message = f'''Estimado/a {encargado.first_name or encargado.username},

Tienes una nueva solicitud que requiere tu atención en el Sistema de Gestión UABJB.

📋 DETALLES DE LA SOLICITUD:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👤 SOLICITANTE:
- Nombre: {solicitante_nombre}
- Email: {solicitud.usuario_solicitante.email}
- Teléfono: {solicitud.usuario_solicitante.telefono or 'No especificado'}
{info_academica}

🎯 INFORMACIÓN DEL EVENTO:
- Evento: {solicitud.nombre_evento}
- Descripción: {solicitud.descripcion_evento or 'No especificada'}
- Fecha y hora: {fecha_evento_str}
- Espacio solicitado: {solicitud.get_nombre_espacio()}
- Tipo de espacio: {solicitud.get_tipo_espacio_display()}

📅 INFORMACIÓN DE LA SOLICITUD:
- Estado: {solicitud.get_estado_display()}
- Fecha de solicitud: {fecha_creacion_str}
- Archivo adjunto: {'Sí' if solicitud.archivo_adjunto else 'No'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚡ ACCIÓN REQUERIDA:
Por favor, revisa tu dashboard para aprobar o rechazar esta solicitud.

📱 Dashboard → Ver Solicitudes → Solicitudes Pendientes

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Este es un correo automático del Sistema de Gestión UABJB.

Saludos cordiales,
Sistema de Gestión UABJB'''
        
        # Enviar el correo
        send_mail(
            subject,
            message,
            'cibanezsanguino@gmail.com',  # From email (el mismo que usas actualmente)
            [encargado.email],  # To email
            fail_silently=True,  # No rompe el sistema si falla el correo
        )
        
        print(f'✅ Notificación enviada al encargado {encargado.email} para la solicitud: {solicitud.nombre_evento}')
        
    except Exception as e:
        print(f'❌ Error enviando notificación al encargado: {str(e)}')


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
    # Espacios de la facultad a la que pertenece el usuario
    espacios_carrera = Espacio.objects.filter(
        activo=True,
        carrera__facultad=request.user.carrera.facultad   # <-- relación real
    )

    # Todos los espacios del campus (sin filtro de facultad)
    espacios_campus = EspacioCampus.objects.all()

    # Unimos ambas listas para la plantilla
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
            # Crear la solicitud
            nueva_solicitud = Solicitud.objects.create(
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
            
            # 🔔 ENVIAR NOTIFICACIÓN AL ENCARGADO
            print(f'📧 Enviando notificación para nueva solicitud: {nueva_solicitud.nombre_evento}')
            notificar_nueva_solicitud(nueva_solicitud)
            
            messages.success(request, '¡Solicitud enviada con éxito!')
            return redirect('usuarios:usuario')

    return render(request, 'usuarios/enviar_solicitud.html', {
        'espacios_carrera': espacios_carrera,
        'espacios_campus': espacios_campus,
    })

@login_required
def eventos_usuario_json(request):
    user = request.user

    ids_carrera = Espacio.objects.filter(carrera=user.carrera).values_list('id', flat=True)
    ids_facultad = Espacio.objects.filter(carrera__facultad=user.facultad).values_list('id', flat=True)
    ids_campus = EspacioCampus.objects.all().values_list('id', flat=True)

    eventos = Solicitud.objects.filter(
        estado='aceptada',
        usuario_solicitante=user
    ).filter(
        Q(tipo_espacio='carrera', espacio_id__in=ids_carrera) |
        Q(tipo_espacio='carrera', espacio_id__in=ids_facultad) |
        Q(tipo_espacio='campus', espacio_campus_id__in=ids_campus)
    ).select_related('espacio', 'espacio_campus')

    data = []
    for s in eventos:
        data.append({
            'fecha': s.fecha_evento.strftime('%Y-%m-%d'),
            'nombre_evento': s.nombre_evento,
            'espacio__nombre': s.get_nombre_espacio(),
        })
    
    return JsonResponse(data, safe=False)

@login_required
def perfil_usuario(request):
    """
    Vista para mostrar el perfil del usuario con su información personal
    """
    context = {
        'usuario': request.user,
    }
    return render(request, 'usuarios/perfil_usuario.html', context)

@login_required
def cambiar_contrasena(request):
    """
    Vista para cambiar la contraseña del usuario
    """
    if request.method == 'POST':
        contrasena_actual = request.POST.get('contrasena_actual')
        nueva_contrasena = request.POST.get('nueva_contrasena')
        confirmar_contrasena = request.POST.get('confirmar_contrasena')
        
        # Verificar que la contraseña actual sea correcta
        if not request.user.check_password(contrasena_actual):
            messages.error(request, 'La contraseña actual es incorrecta.')
            return redirect('usuarios:cambiar_contrasena')  # Cambiado aquí
        
        # Verificar que las nuevas contraseñas coincidan
        if nueva_contrasena != confirmar_contrasena:
            messages.error(request, 'Las nuevas contraseñas no coinciden.')
            return redirect('usuarios:cambiar_contrasena')  # Cambiado aquí
        
        # Verificar que la nueva contraseña tenga al menos 8 caracteres
        if len(nueva_contrasena) < 8:
            messages.error(request, 'La nueva contraseña debe tener al menos 8 caracteres.')
            return redirect('usuarios:cambiar_contrasena')  # Cambiado aquí
        
        # Cambiar la contraseña
        request.user.set_password(nueva_contrasena)
        request.user.save()
        
        messages.success(request, '¡Contraseña cambiada exitosamente!')
        return redirect('usuarios:perfil_usuario')
    
    # Manejar GET request - mostrar el formulario
    return render(request, 'usuarios/cambiar_contrasena.html', {
        'usuario': request.user
    })