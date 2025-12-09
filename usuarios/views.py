from django.forms import ValidationError
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from gestion_espacios_academicos import settings
from gestion_espacios_academicos.models import Espacio, EspacioCampus, Solicitud
from django.http import JsonResponse
from django.db.models import Q
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.dateparse import parse_datetime
from datetime import datetime
from usuarios.forms import EditarPerfilForm
import hashlib
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import qrcode
import uuid
from io import BytesIO
from base64 import b64encode
from django.core.mail import EmailMultiAlternatives
import hashlib
from zoneinfo import ZoneInfo
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from io import BytesIO
from django.core.files.base import ContentFile
from django.views.decorators.http import require_http_methods
from datetime import datetime, timedelta
import json
from django.views.decorators.cache import never_cache

# ✅ FIX 1: Vista de Usuario con validación y anti-cache
@login_required
@never_cache  # 🔥 CRÍTICO: No cachear
def usuario(request):
    """
    Dashboard del usuario regular
    """
    user = request.user
    
    # 🔒 Verificar que sea usuario regular
    if user.tipo_usuario != 'usuario':
        messages.error(request, '⛔ No tienes permiso para acceder a esta página.')
        return redirect('login')
    
    # 🔍 Debug: Verificar sesión
    print(f"👤 Dashboard Usuario: {user.username} (ID: {user.id}, Rol: {user.tipo_usuario})")
    print(f"   Session Key: {request.session.session_key}")
    
    context = {
        'mes_actual': timezone.now().strftime('%B %Y'),
        'usuario': user,  # ✅ Pasar usuario explícitamente
        'session_key': request.session.session_key[:10],  # Para debugging
    }
    
    return render(request, 'usuarios/usuario.html', context)

# Zona horaria fija de Bolivia (una sola vez)
TZ_BOLIVIA = ZoneInfo("America/La_Paz")

def ahora_bolivia():
    """Devuelve datetime.now() en hora de Bolivia (aware)"""
    return timezone.now().astimezone(TZ_BOLIVIA)

def to_bolivia(dt):
    """Convierte cualquier datetime aware a hora de Bolivia"""
    if dt is None:
        return None
    return dt.astimezone(TZ_BOLIVIA)

# ============================
# FUNCIONES DE CONFIRMACIÓN
# ============================

def generar_token_confirmacion(solicitud_id, usuario_id, fecha_evento):
    """
    Genera un token único SHA256 para la confirmación de solicitud aceptada.
    AHORA USA HORA DE BOLIVIA EN LUGAR DE UTC
    """
    # Usar hora local de Bolivia para el timestamp
    timestamp = ahora_bolivia().isoformat()
    data = f"{solicitud_id}-{usuario_id}-{fecha_evento}-{timestamp}"
    token = hashlib.sha256(data.encode()).hexdigest()[:16].upper()
    return token

def generar_qr_confirmacion(solicitud, token):
    """
    Genera un código QR con la información de confirmación.
    El QR contiene: ID de solicitud + Token + Fecha del evento
    """
    try:
        print(f"🎨 Iniciando generación de QR...")
        print(f"   Solicitud ID: {solicitud.id}")
        print(f"   Token: {token}")
        
        # Información que irá en el QR
        fecha_qr = to_bolivia(solicitud.fecha_evento).strftime("%d/%m/%Y %H:%M")
        qr_data = f"SOLICITUD:{solicitud.id}|TOKEN:{token}|FECHA:{fecha_qr}|USER:{solicitud.usuario_solicitante.username}"
        print(f"   Datos QR: {qr_data[:50]}...")
        
        # Crear el QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=2,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        print(f"✅ QR object creado")
        
        # Convertir a imagen
        img = qr.make_image(fill_color="black", back_color="white")
        print(f"✅ Imagen generada")
        
        # Convertir a base64 para embeber en HTML
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)  # 🔧 IMPORTANTE: Regresar al inicio del buffer
        img_str = b64encode(buffer.getvalue()).decode()
        
        print(f"✅ QR convertido a base64 (longitud: {len(img_str)} caracteres)")
        
        return img_str
        
    except Exception as e:
        print(f"❌ Error generando QR: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def notificar_aceptacion_solicitud(solicitud, encargado=None):
    """
    Envía correo de confirmación al solicitante cuando su solicitud es ACEPTADA.
    Incluye: Token único + Código QR + Detalles del evento
    """
    try:
        import pytz
        user = solicitud.usuario_solicitante
        
        if not user.email:
            print(f"⚠️ El usuario {user.username} no tiene email configurado")
            return False
        
        # 1️⃣ GENERAR TOKEN DE CONFIRMACIÓN
        token = generar_token_confirmacion(
            solicitud.id,
            user.id,
            solicitud.fecha_evento.isoformat()
        )
        
        # Guardar token en la solicitud
        solicitud.token_confirmacion = token
        solicitud.fecha_confirmacion = timezone.now()
        solicitud.save(update_fields=['token_confirmacion', 'fecha_confirmacion'])
        
        # 2️⃣ GENERAR CÓDIGO QR
        qr_base64 = generar_qr_confirmacion(solicitud, token)
        
        # 3️⃣ PREPARAR INFORMACIÓN DEL EVENTO CON ZONA HORARIA CORRECTA
        # ✅ CORRECCIÓN: Convertir a zona horaria de Bolivia
        bolivia_tz = pytz.timezone('America/La_Paz')
        
        fecha_evento_bolivia = solicitud.fecha_evento.astimezone(bolivia_tz)
        fecha_evento_str = fecha_evento_bolivia.strftime("%d/%m/%Y a las %H:%M")

        if solicitud.fecha_fin_evento:
            fecha_fin_bolivia = solicitud.fecha_fin_evento.astimezone(bolivia_tz)
            fecha_fin_str = fecha_fin_bolivia.strftime("%d/%m/%Y a las %H:%M")
        else:
            fecha_fin_str = None
        
        # ✅ CORRECCIÓN: Obtener el nombre CORRECTO del espacio
        if solicitud.tipo_espacio == 'carrera' and solicitud.espacio:
            espacio_nombre = solicitud.espacio.nombre  # ✅ Nombre del ESPACIO, no de la carrera
            # Mostrar también la carrera en el tipo
            if solicitud.espacio.carrera:
                tipo_espacio_display = f"Espacio de Carrera - {solicitud.espacio.carrera.nombre}"
            else:
                tipo_espacio_display = "Espacio de Carrera"
        elif solicitud.tipo_espacio == 'campus' and solicitud.espacio_campus:
            espacio_nombre = solicitud.espacio_campus.nombre  # ✅ Nombre del espacio de campus
            tipo_espacio_display = "Espacio de Campus"
        else:
            espacio_nombre = "No especificado"
            tipo_espacio_display = "No especificado"
        
        solicitante_nombre = user.get_full_name() or user.username
        
        # 4️⃣ CONTEXTO PARA EL TEMPLATE
        context = {
            'solicitud': solicitud,
            'user': user,
            'solicitante_nombre': solicitante_nombre,
            'nombre_evento': solicitud.nombre_evento,
            'descripcion_evento': solicitud.descripcion_evento,
            'fecha_evento': fecha_evento_str,
            'fecha_fin_evento': fecha_fin_str,
            'espacio_nombre': espacio_nombre,
            'tipo_espacio': tipo_espacio_display,
            'token': token,
            'qr_base64': None,  # Ya no usamos base64 en el template
            'encargado_nombre': encargado.get_full_name() if encargado else 'Encargado del espacio',
        }
        
        # 5️⃣ RENDERIZAR HTML DEL CORREO
        html_message = render_to_string('usuarios/confirmacion_aceptacion.html', context)
        
        # 6️⃣ ENVIAR CORREO CON QR ADJUNTO
        subject = f"✅ ¡Solicitud Aceptada! - {solicitud.nombre_evento}"
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=f"Tu solicitud '{solicitud.nombre_evento}' ha sido ACEPTADA. Token: {token}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        
        email.attach_alternative(html_message, "text/html")
        
        # 🔑 ADJUNTAR QR COMO IMAGEN INLINE
        if qr_base64:
            from email.mime.image import MIMEImage
            import base64
            
            qr_data = base64.b64decode(qr_base64)
            qr_image = MIMEImage(qr_data)
            qr_image.add_header('Content-ID', '<qr_code>')
            qr_image.add_header('Content-Disposition', 'inline', filename='qr_code.png')
            email.attach(qr_image)
        
        email.send(fail_silently=False)
        
        print(f"✅ Confirmación de aceptación enviada a {user.email}")
        print(f"   Token: {token}")
        print(f"   Espacio: {espacio_nombre}")
        print(f"   Fecha (Bolivia): {fecha_evento_str}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error enviando confirmación de aceptación: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
@login_required
@require_http_methods(["POST"])
def verificar_conflictos_antes_enviar(request):
    """
    Verifica si hay conflictos de horario ANTES de que el usuario envíe la solicitud.
    """
    try:
        # ✅ PERMITIR TANTO JSON COMO FORM DATA
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST
        
        # ✅ DEBUG: Imprimir lo que recibimos
        print("=" * 50)
        print("📥 VERIFICACIÓN DE CONFLICTOS RECIBIDA")
        print(f"   Content-Type: {request.content_type}")
        print(f"   Usuario: {request.user.username}")
        print(f"   Datos: {data}")
        print("=" * 50)
        
        fecha_evento_str = data.get('fecha_evento')
        fecha_fin_evento_str = data.get('fecha_fin_evento')
        tipo_espacio = data.get('tipo_espacio')
        espacio_id = data.get('espacio_carrera') if tipo_espacio == 'carrera' else data.get('espacio_campus')
        
        # Validaciones básicas
        if not all([fecha_evento_str, tipo_espacio, espacio_id]):
            return JsonResponse({
                'status': 'error',
                'message': 'Faltan datos requeridos'
            }, status=400)
        
        # Parsear fechas
        try:
            fecha_inicio = datetime.strptime(fecha_evento_str, '%Y-%m-%dT%H:%M')
            fecha_inicio = timezone.make_aware(fecha_inicio)
            
            if fecha_fin_evento_str:
                fecha_fin = datetime.strptime(fecha_fin_evento_str, '%Y-%m-%dT%H:%M')
                fecha_fin = timezone.make_aware(fecha_fin)
            else:
                # Si no hay fecha fin, asumir 2 horas
                fecha_fin = fecha_inicio + timedelta(hours=2)
        except ValueError as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Formato de fecha inválido: {str(e)}'
            }, status=400)
        
        # Buscar solicitudes aceptadas en el mismo espacio
        query_base = Solicitud.objects.filter(
            estado='aceptada',
            eliminada=False
        )
        
        if tipo_espacio == 'carrera':
            query_base = query_base.filter(
                tipo_espacio='carrera',
                espacio_id=espacio_id
            )
        else:
            query_base = query_base.filter(
                tipo_espacio='campus',
                espacio_campus_id=espacio_id
            )
        
        # Verificar conflictos
        conflictos = []
        
        for solicitud in query_base:
            otra_inicio = solicitud.fecha_evento
            
            if solicitud.fecha_fin_evento:
                otra_fin = solicitud.fecha_fin_evento
            else:
                otra_fin = solicitud.fecha_evento + timedelta(hours=2)
            
            # Verificar si hay solapamiento
            if fecha_inicio < otra_fin and fecha_fin > otra_inicio:
                import pytz
                bolivia_tz = pytz.timezone('America/La_Paz')
                
                inicio_bolivia = otra_inicio.astimezone(bolivia_tz)
                fin_bolivia = otra_fin.astimezone(bolivia_tz)
                
                conflictos.append({
                    'nombre_evento': solicitud.nombre_evento,
                    'solicitante': solicitud.usuario_solicitante.get_full_name() or solicitud.usuario_solicitante.username,
                    'fecha_inicio': inicio_bolivia.strftime('%d/%m/%Y %H:%M'),
                    'fecha_fin': fin_bolivia.strftime('%d/%m/%Y %H:%M'),
                    'es_propio': solicitud.usuario_solicitante == request.user
                })
        
        if conflictos:
            return JsonResponse({
                'status': 'warning',
                'tiene_conflictos': True,
                'mensaje': f'⚠️ Hay {len(conflictos)} reserva(s) aceptada(s) en este horario',
                'conflictos': conflictos
            })
        else:
            return JsonResponse({
                'status': 'success',
                'tiene_conflictos': False,
                'mensaje': '✅ No hay conflictos de horario'
            })
        
    except Exception as e:
        print(f"❌ Error verificando conflictos: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'status': 'error',
            'message': f'Error al verificar conflictos: {str(e)}'
        }, status=500)

def notificar_rechazo_solicitud(solicitud, motivo=""):
    """
    Envía correo al solicitante cuando su solicitud es RECHAZADA
    """
    try:
        user = solicitud.usuario_solicitante
        
        if not user.email:
            return False
        
        subject = f"❌ Solicitud Rechazada - {solicitud.nombre_evento}"
        
        context = {
            'solicitud': solicitud,
            'user': user,
            'nombre_evento': solicitud.nombre_evento,
            'fecha_evento': solicitud.fecha_evento.strftime("%d/%m/%Y a las %H:%M"),
            'espacio_nombre': solicitud.get_nombre_espacio(),
            'motivo': solicitud.motivo_rechazo or motivo or "No especificado",
        }
        
        html_message = render_to_string('usuarios/confirmacion_rechazo.html', context)
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=f"Tu solicitud '{solicitud.nombre_evento}' ha sido rechazada.",
            from_email='cibanezsanguino@gmail.com',
            to=[user.email],
        )
        
        email.attach_alternative(html_message, "text/html")
        email.send(fail_silently=False)
        
        print(f"✅ Notificación de rechazo enviada a {user.email}")
        return True
        
    except Exception as e:
        print(f"❌ Error enviando notificación de rechazo: {str(e)}")
        return False

def notificar_confirmacion_solicitud(solicitud, request):
    try:
        import pytz
        
        user = solicitud.usuario_solicitante
        if not user.email:
            print("⚠️ El usuario no tiene email configurado")
            return False

        protocol = 'https' if request.is_secure() else 'http'
        domain = request.get_host()
        enlace_estado = f"{protocol}://{domain}/usuarios/historial-solicitudes/"

        # ✅ CONFIGURAR ZONA HORARIA DE BOLIVIA
        bolivia_tz = pytz.timezone('America/La_Paz')
        
        # 🔧 FIX: Convertir fecha_evento a hora de Bolivia CORRECTAMENTE
        if isinstance(solicitud.fecha_evento, str):
            try:
                # Parsear el string a datetime
                fecha_obj = parse_datetime(solicitud.fecha_evento)
                if fecha_obj:
                    # ✅ CRITICAL: Si es naive, asumimos que YA ESTÁ en hora de Bolivia
                    if timezone.is_naive(fecha_obj):
                        # Lo hacemos aware directamente con la zona horaria de Bolivia
                        fecha_bolivia = bolivia_tz.localize(fecha_obj)
                    else:
                        # Si ya es aware, solo convertimos a Bolivia
                        fecha_bolivia = fecha_obj.astimezone(bolivia_tz)
                    
                    fecha_evento = fecha_bolivia.strftime("%d/%m/%Y a las %H:%M")
                else:
                    fecha_evento = solicitud.fecha_evento
            except Exception as e:
                print(f"⚠️ Error al parsear fecha: {e}")
                fecha_evento = solicitud.fecha_evento
        else:
            # Si ya es datetime
            if timezone.is_naive(solicitud.fecha_evento):
                # ✅ CRITICAL: Asumimos que es hora de Bolivia
                fecha_bolivia = bolivia_tz.localize(solicitud.fecha_evento)
            else:
                # Si ya es aware, convertimos a Bolivia
                fecha_bolivia = solicitud.fecha_evento.astimezone(bolivia_tz)
            
            fecha_evento = fecha_bolivia.strftime("%d/%m/%Y a las %H:%M")
        
        # ✅ Convertir fecha de creación de la solicitud a Bolivia
        if timezone.is_naive(solicitud.fecha_creacion):
            fecha_creacion_bolivia = bolivia_tz.localize(solicitud.fecha_creacion)
        else:
            fecha_creacion_bolivia = solicitud.fecha_creacion.astimezone(bolivia_tz)
        
        fecha_solicitud = fecha_creacion_bolivia.strftime("%d/%m/%Y a las %H:%M")
        
        espacio_nombre = solicitud.get_nombre_espacio()
        tiene_archivo = bool(solicitud.archivo_adjunto)

        html_message = render_to_string('usuarios/confirmacion_solicitud.html', {
            'solicitud': solicitud,
            'user': user,
            'enlace_estado': enlace_estado,
            'fecha_evento': fecha_evento,
            'fecha_solicitud': fecha_solicitud,
            'espacio_nombre': espacio_nombre,
            'tiene_archivo': tiene_archivo,
        })

        subject = "✅ Solicitud recibida - Sistema UABJB"

        send_mail(
            subject,
            None,
            settings.EMAIL_HOST_USER,
            [user.email],
            html_message=html_message,
            fail_silently=False,
        )
        print(f"✅ Confirmación HTML enviada a {user.email}")
        print(f"   Fecha evento (Bolivia): {fecha_evento}")
        print(f"   Fecha solicitud (Bolivia): {fecha_solicitud}")
        return True
    except Exception as e:
        print(f"❌ Error enviando confirmación HTML: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

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

def generar_token_solicitud(user_id, nombre_evento, fecha_evento, espacio_id):
    """
    Genera un token único para identificar solicitudes duplicadas.
    Combina: usuario + nombre evento + fecha + espacio
    """
    data = f"{user_id}-{nombre_evento}-{fecha_evento}-{espacio_id}"
    return hashlib.md5(data.encode()).hexdigest()

def generar_pdf_terminos_aceptados(solicitud):
    """
    Genera un PDF con los términos aceptados, firma digital y código QR de verificación
    Retorna el PDF como BytesIO
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, 
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    # Contenedor para los elementos
    elementos = []
    styles = getSampleStyleSheet()
    
    # Estilo personalizado para el título
    titulo_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Estilo para subtítulos
    subtitulo_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#4a5568'),
        spaceAfter=12,
        spaceBefore=20,
        fontName='Helvetica-Bold'
    )
    
    # Estilo para texto normal
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#2d3748'),
        alignment=TA_JUSTIFY,
        spaceAfter=10
    )
    
    # === ENCABEZADO ===
    elementos.append(Paragraph("UNIVERSIDAD AUTÓNOMA DEL BENI<br/>JOSÉ BALLIVIÁN", titulo_style))
    elementos.append(Spacer(1, 0.3*inch))
    
    elementos.append(Paragraph("CONSTANCIA DE ACEPTACIÓN DE TÉRMINOS Y CONDICIONES", subtitulo_style))
    elementos.append(Spacer(1, 0.2*inch))
    
    # === INFORMACIÓN DEL EVENTO ===
    fecha_evento = to_bolivia(solicitud.fecha_evento).strftime("%d/%m/%Y %H:%M")
    fecha_aceptacion = to_bolivia(solicitud.fecha_aceptacion_terminos).strftime("%d/%m/%Y %H:%M:%S")
    
    info_data = [
        ['Solicitud ID:', str(solicitud.id)],
        ['Evento:', solicitud.nombre_evento],
        ['Solicitante:', solicitud.usuario_solicitante.get_full_name() or solicitud.usuario_solicitante.username],
        ['Email:', solicitud.usuario_solicitante.email],
        ['Carrera:', solicitud.usuario_solicitante.carrera or 'N/A'],
        ['Espacio:', solicitud.get_nombre_espacio()],
        ['Fecha del Evento:', fecha_evento],
        ['Fecha de Aceptación:', fecha_aceptacion],
        ['Dirección IP:', solicitud.ip_aceptacion or 'N/A'],
    ]
    
    tabla_info = Table(info_data, colWidths=[2*inch, 4*inch])
    tabla_info.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e2e8f0')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2d3748')),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    elementos.append(tabla_info)
    elementos.append(Spacer(1, 0.3*inch))
    
    # === DOCUMENTOS ACEPTADOS ===
    elementos.append(Paragraph("DOCUMENTOS ACEPTADOS", subtitulo_style))
    
    documentos_data = [
        ['✓', 'Condiciones de Uso de Espacios del Campus'],
        ['✓', 'Ley 259 - Control al Expendio y Consumo de Bebidas Alcohólicas'],
    ]
    
    tabla_docs = Table(documentos_data, colWidths=[0.5*inch, 5.5*inch])
    tabla_docs.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0fff4')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#38a169')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#2d3748')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (0, -1), 16),
        ('FONTSIZE', (1, 0), (1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#9ae6b4')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    
    elementos.append(tabla_docs)
    elementos.append(Spacer(1, 0.3*inch))
    
    # === FIRMA DIGITAL ===
    elementos.append(Paragraph("FIRMA DIGITAL DEL SOLICITANTE", subtitulo_style))
    
    if solicitud.firma_digital:
        try:
            # Agregar la firma como imagen
            firma_img = Image(solicitud.firma_digital.path, width=3*inch, height=1.5*inch)
            firma_img.hAlign = 'CENTER'
            elementos.append(firma_img)
        except Exception as e:
            print(f"⚠️ No se pudo cargar la firma: {e}")
            elementos.append(Paragraph("Firma no disponible", normal_style))
    else:
        elementos.append(Paragraph("Sin firma digital", normal_style))
    
    elementos.append(Spacer(1, 0.2*inch))
    
    # Línea de firma
    firma_line = Table([['_' * 50]], colWidths=[4*inch])
    firma_line.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
    ]))
    elementos.append(firma_line)
    
    firma_texto = Paragraph(
        f"<b>{solicitud.usuario_solicitante.get_full_name() or solicitud.usuario_solicitante.username}</b><br/>"
        f"<i>Firma Digital Electrónica</i>",
        normal_style
    )
    elementos.append(firma_texto)
    elementos.append(Spacer(1, 0.3*inch))
    
    # === CÓDIGO QR DE VERIFICACIÓN ===
    elementos.append(Paragraph("CÓDIGO DE VERIFICACIÓN", subtitulo_style))
    
    # Generar QR con datos de verificación
    qr_data = f"VERIFY:{solicitud.id}|USER:{solicitud.usuario_solicitante.username}|DATE:{fecha_aceptacion}|IP:{solicitud.ip_aceptacion}"
    
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(qr_data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    # Guardar QR en buffer
    qr_buffer = BytesIO()
    qr_img.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)
    
    # Agregar QR al PDF
    qr_image = Image(qr_buffer, width=2*inch, height=2*inch)
    qr_image.hAlign = 'CENTER'
    elementos.append(qr_image)
    
    elementos.append(Spacer(1, 0.1*inch))
    
    verificacion_texto = Paragraph(
        "<i>Escanea este código QR para verificar la autenticidad de este documento</i>",
        ParagraphStyle('Center', parent=normal_style, alignment=TA_CENTER, fontSize=8)
    )
    elementos.append(verificacion_texto)
    elementos.append(Spacer(1, 0.3*inch))
    
    # === PIE DE PÁGINA ===
    pie_texto = Paragraph(
        f"<i>Documento generado electrónicamente el {ahora_bolivia().strftime('%d/%m/%Y %H:%M:%S')} (Hora de Bolivia)<br/>"
        f"Este documento tiene validez legal conforme a la normativa vigente de la UABJB.<br/>"
        f"ID de Verificación: {solicitud.id}-{solicitud.usuario_solicitante.id}</i>",
        ParagraphStyle('Footer', parent=normal_style, fontSize=8, textColor=colors.HexColor('#718096'), alignment=TA_CENTER)
    )
    elementos.append(pie_texto)
    
    # Construir PDF
    doc.build(elementos)
    
    buffer.seek(0)
    return buffer


def enviar_email_terminos_aceptados(solicitud, encargado=None):
    """
    Envía email al usuario con PDF de términos aceptados
    También copia al encargado del espacio
    """
    try:
        user = solicitud.usuario_solicitante
        
        if not user.email:
            print(f"⚠️ El usuario {user.username} no tiene email")
            return False
        
        # Generar PDF
        pdf_buffer = generar_pdf_terminos_aceptados(solicitud)
        
        # Preparar el email
        fecha_evento = to_bolivia(solicitud.fecha_evento).strftime("%d/%m/%Y %H:%M")
        
        subject = f"📄 Términos Aceptados - {solicitud.nombre_evento}"
        
        body = f"""Estimado/a {user.get_full_name() or user.username},

Confirmamos que has aceptado los términos y condiciones para el uso del espacio:

📋 DETALLES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Evento: {solicitud.nombre_evento}
• Espacio: {solicitud.get_nombre_espacio()}
• Fecha: {fecha_evento}

✅ DOCUMENTOS ACEPTADOS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Condiciones de Uso de Espacios del Campus
• Ley 259 - Control al Expendio y Consumo de Bebidas Alcohólicas

✍️ FIRMA DIGITAL:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Tu firma digital ha sido registrada exitosamente.

📎 DOCUMENTO ADJUNTO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Adjuntamos una constancia en PDF con tu firma digital y código QR 
de verificación. Este documento es tu comprobante oficial.

IMPORTANTE: Conserva este documento como respaldo de tu compromiso 
con las normativas del campus universitario.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Saludos cordiales,
Sistema de Gestión UABJB"""
        
        # Crear email con alternativas
        email = EmailMultiAlternatives(
            subject=subject,
            body=body,
            from_email='cibanezsanguino@gmail.com',
            to=[user.email],
        )
        
        # Adjuntar PDF
        pdf_filename = f"terminos_aceptados_{solicitud.id}_{user.username}.pdf"
        email.attach(pdf_filename, pdf_buffer.getvalue(), 'application/pdf')
        
        # Si hay encargado, agregarlo en copia
        if encargado and encargado.email:
            email.cc = [encargado.email]
        
        email.send(fail_silently=False)
        
        print(f"✅ Email con PDF enviado a {user.email}")
        if encargado and encargado.email:
            print(f"   📋 Copia enviada a encargado: {encargado.email}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error enviando email con PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

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
        
        acepta_condiciones = request.POST.get('acepta_condiciones_uso') == 'on'
        
        token_form = request.POST.get('form_token')
        token_session = request.session.get('last_form_token')
        
        if token_form and token_form == token_session:
            messages.warning(request, '⚠️ Esta solicitud ya fue enviada.')
            return redirect('usuarios:historial_solicitudes')

        errores = []
        if not nombre_evento: errores.append('Nombre obligatorio.')
        if not fecha_evento:  errores.append('Fecha obligatoria.')
        if not archivo_adjunto: errores.append('Archivo obligatorio.')
        if tipo_espacio == 'carrera' and not espacio_carrera: 
            errores.append('Selecciona carrera.')
        if tipo_espacio == 'campus' and not espacio_campus:   
            errores.append('Selecciona campus.')
        
        # ✅ VALIDAR QUE EXISTA DOCUMENTO DE CONDICIONES PARA ESPACIOS DE CAMPUS
        if tipo_espacio == 'campus' and espacio_campus:
            try:
                espacio_obj = EspacioCampus.objects.get(id=espacio_campus)
                if not espacio_obj.documento_condiciones:
                    errores.append('⚠️ Este espacio no tiene documento de condiciones disponible.')
            except EspacioCampus.DoesNotExist:
                errores.append('❌ Espacio no válido.')
            
            if not acepta_condiciones:
                errores.append('❌ Debes aceptar las Condiciones de Uso.')

        if errores:
            for e in errores: 
                messages.error(request, e)
        else:
            espacio_id = espacio_carrera if tipo_espacio == 'carrera' else espacio_campus
            
            cinco_minutos_atras = timezone.now() - timezone.timedelta(minutes=5)
            solicitud_existente = Solicitud.objects.filter(
                usuario_solicitante=request.user,
                nombre_evento=nombre_evento,
                fecha_evento=fecha_evento,
                tipo_espacio=tipo_espacio,
                fecha_creacion__gte=cinco_minutos_atras
            )
            
            if tipo_espacio == 'carrera':
                solicitud_existente = solicitud_existente.filter(espacio_id=espacio_carrera)
            else:
                solicitud_existente = solicitud_existente.filter(espacio_campus_id=espacio_campus)
            
            if solicitud_existente.exists():
                messages.warning(request, 
                    '⚠️ Ya enviaste una solicitud idéntica hace menos de 5 minutos.')
                return redirect('usuarios:historial_solicitudes')
            
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
                acepta_condiciones_uso=acepta_condiciones if tipo_espacio == 'campus' else False,
                fecha_aceptacion_terminos=timezone.now() if tipo_espacio == 'campus' and acepta_condiciones else None,
                ip_aceptacion=obtener_ip_cliente(request) if tipo_espacio == 'campus' and acepta_condiciones else None,
            )
            
            token_unico = generar_token_solicitud(
                request.user.id,
                nombre_evento,
                fecha_evento,
                espacio_id
            )
            
            request.session['last_form_token'] = token_unico
            request.session['last_solicitud_id'] = nueva_solicitud.id
                        
            print(f'📧 Enviando notificación para: {nueva_solicitud.nombre_evento}')
            notificar_nueva_solicitud(nueva_solicitud)
            notificar_confirmacion_solicitud(nueva_solicitud, request)
            
            mensaje_exito = '✅ ¡Solicitud enviada con éxito!'
            if tipo_espacio == 'campus' and acepta_condiciones:
                mensaje_exito += ' Términos y condiciones aceptados.'
            
            messages.success(request, mensaje_exito)
            return redirect('usuarios:historial_solicitudes')
    
    import uuid
    form_token = str(uuid.uuid4())

    return render(request, 'usuarios/enviar_solicitud.html', {
        'espacios_carrera': espacios_carrera,
        'espacios_campus': espacios_campus,
        'form_token': form_token,
    })

from django.http import JsonResponse

@login_required
def obtener_documento_espacio(request, espacio_id):
    """Devuelve la URL del documento de condiciones del espacio"""
    try:
        espacio = EspacioCampus.objects.get(id=espacio_id)
        if espacio.documento_condiciones:
            return JsonResponse({
                'success': True,
                'documento_url': espacio.documento_condiciones.url,
                'tiene_documento': True
            })
        else:
            return JsonResponse({
                'success': True,
                'tiene_documento': False,
                'mensaje': 'Este espacio no tiene documento de condiciones'
            })
    except EspacioCampus.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Espacio no encontrado'
        }, status=404)

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
        
        # 🆕 INFORMACIÓN SOBRE ACEPTACIÓN DE CONDICIONES (solo para campus)
        info_condiciones = ""
        if solicitud.tipo_espacio == 'campus':
            if solicitud.acepta_condiciones_uso:
                import pytz
                bolivia_tz = pytz.timezone('America/La_Paz')
                
                fecha_aceptacion = solicitud.fecha_aceptacion_terminos
                if fecha_aceptacion:
                    if timezone.is_naive(fecha_aceptacion):
                        fecha_aceptacion = timezone.make_aware(fecha_aceptacion)
                    fecha_aceptacion_bolivia = fecha_aceptacion.astimezone(bolivia_tz)
                    fecha_aceptacion_str = fecha_aceptacion_bolivia.strftime("%d/%m/%Y a las %H:%M:%S")
                else:
                    fecha_aceptacion_str = "No registrada"
                
                info_condiciones = f'''
✅ CONDICIONES DE USO ACEPTADAS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- El solicitante ha aceptado las Condiciones de Uso del Campus
- Fecha de aceptación: {fecha_aceptacion_str}
- IP de aceptación: {solicitud.ip_aceptacion or 'No registrada'}
- Documentos aceptados:
  • Condiciones de Uso de Espacios del Campus
  • Ley 259 - Control al Expendio y Consumo de Bebidas Alcohólicas

'''
            else:
                info_condiciones = '''
⚠️  NOTA: Este espacio de campus no requirió aceptación de condiciones.

'''
        
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
- Archivo adjunto: {'Sí' if solicitud.archivo_adjunto else 'No'}

{info_condiciones}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

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
            'cibanezsanguino@gmail.com',
            [encargado.email],
            fail_silently=True,
        )
        
        print(f'✅ Notificación enviada al encargado {encargado.email} para la solicitud: {solicitud.nombre_evento}')
        if solicitud.tipo_espacio == 'campus' and solicitud.acepta_condiciones_uso:
            print(f'   ✓ Incluye información de aceptación de condiciones')
        
    except Exception as e:
        print(f'❌ Error enviando notificación al encargado: {str(e)}')
        import traceback
        traceback.print_exc()


# 🆕 FUNCIÓN AUXILIAR PARA OBTENER IP
def obtener_ip_cliente(request):
    """Obtiene la IP real del cliente (incluso detrás de proxies)"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@login_required
def eventos_usuario_json(request):
    """
    Retorna TODAS las solicitudes aceptadas de los espacios relevantes para el usuario
    INCLUYE LA HORA DEL EVENTO
    """
    import pytz
    user = request.user

    # Obtener IDs de los espacios relevantes
    ids_carrera = Espacio.objects.filter(carrera=user.carrera).values_list('id', flat=True)
    ids_facultad = Espacio.objects.filter(carrera__facultad=user.facultad).values_list('id', flat=True)
    ids_campus = EspacioCampus.objects.all().values_list('id', flat=True)

    eventos = Solicitud.objects.filter(
        estado='aceptada'
    ).filter(
        Q(tipo_espacio='carrera', espacio_id__in=ids_carrera) |
        Q(tipo_espacio='carrera', espacio_id__in=ids_facultad) |
        Q(tipo_espacio='campus', espacio_campus_id__in=ids_campus)
    ).select_related('espacio', 'espacio_campus', 'usuario_solicitante')

    data = []
    bolivia_tz = pytz.timezone('America/La_Paz')
    
    for s in eventos:
        es_del_usuario = (s.usuario_solicitante == user)
        nombre_solicitante = s.usuario_solicitante.get_full_name() or s.usuario_solicitante.username
        
        # ✅ Obtener el nombre REAL del espacio
        if s.tipo_espacio == 'carrera' and s.espacio:
            nombre_espacio = s.espacio.nombre
        elif s.tipo_espacio == 'campus' and s.espacio_campus:
            nombre_espacio = s.espacio_campus.nombre
        else:
            nombre_espacio = "No especificado"
        
        # ✅ CONVERTIR A HORA DE BOLIVIA
        fecha_evento_bolivia = s.fecha_evento.astimezone(bolivia_tz)
        
        # ✅ AGREGAR HORA FORMATEADA
        hora_inicio = fecha_evento_bolivia.strftime('%H:%M')  # Formato 24 horas: "14:30"
        
        # ✅ Si hay fecha fin, también incluirla
        if s.fecha_fin_evento:
            fecha_fin_bolivia = s.fecha_fin_evento.astimezone(bolivia_tz)
            hora_fin = fecha_fin_bolivia.strftime('%H:%M')
            hora_completa = f"{hora_inicio} - {hora_fin}"
        else:
            hora_completa = hora_inicio
        
        data.append({
            'id': s.id,
            'fecha': fecha_evento_bolivia.strftime('%Y-%m-%d'),
            'fecha_completa': fecha_evento_bolivia.strftime('%Y-%m-%d %H:%M'),
            'fecha_fin': s.fecha_fin_evento.astimezone(bolivia_tz).strftime('%Y-%m-%d %H:%M') if s.fecha_fin_evento else None,
            'hora': hora_completa,  # ✅ NUEVA PROPIEDAD CON LA HORA
            'nombre_evento': s.nombre_evento,
            'espacio__nombre': nombre_espacio,
            'tipo_espacio': s.get_tipo_espacio_display(),
            'solicitante': nombre_solicitante,
            'es_mio': es_del_usuario,
            'descripcion': s.descripcion_evento or '',
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
def editar_perfil(request):
    if request.method == 'POST':
        form = EditarPerfilForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Perfil actualizado con éxito.')
            return redirect('usuarios:perfil_usuario')
    else:
        form = EditarPerfilForm(instance=request.user)

    return render(request, 'usuarios/editar_perfil.html', {'form': form})

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

@login_required
def historial_solicitudes(request):
    solicitudes = Solicitud.objects.filter(usuario_solicitante=request.user).order_by('-fecha_creacion')
    return render(request, 'usuarios/historial_solicitudes.html', {'solicitudes': solicitudes})

@login_required
def editar_solicitud(request, id):
    solicitud = get_object_or_404(Solicitud, id=id, usuario_solicitante=request.user)

    if not solicitud.puede_ser_editada():
        messages.error(request, 'No puedes editar una solicitud que ya fue procesada.')
        return redirect('usuarios:historial_solicitudes')

    if request.method == 'POST':
        # Actualizar campos permitidos
        solicitud.nombre_evento = request.POST.get('nombre_evento', solicitud.nombre_evento)
        solicitud.descripcion_evento = request.POST.get('descripcion_evento', solicitud.descripcion_evento)
        solicitud.fecha_evento = request.POST.get('fecha_evento', solicitud.fecha_evento)
        solicitud.fecha_fin_evento = request.POST.get('fecha_fin_evento') or None
        solicitud.tipo_espacio = request.POST.get('tipo_espacio', solicitud.tipo_espacio)

        if solicitud.tipo_espacio == 'carrera':
            solicitud.espacio_id = request.POST.get('espacio_carrera')
            solicitud.espacio_campus = None
        else:
            solicitud.espacio_campus_id = request.POST.get('espacio_campus')
            solicitud.espacio = None

        if request.FILES.get('archivo_adjunto'):
            solicitud.archivo_adjunto = request.FILES['archivo_adjunto']

        try:
            solicitud.save()
            messages.success(request, 'Solicitud actualizada con éxito.')

            # Notificar al encargado
            notificar_edicion_solicitud(solicitud)

            return redirect('usuarios:historial_solicitudes')
        except ValidationError as e:
            messages.error(request, f'Error al guardar: {e}')

    espacios_carrera = Espacio.objects.filter(activo=True)
    espacios_campus = EspacioCampus.objects.all()

    return render(request, 'usuarios/editar_solicitud.html', {
        'solicitud': solicitud,
        'espacios_carrera': espacios_carrera,
        'espacios_campus': espacios_campus,
    })

@login_required
def cancelar_solicitud(request, id):
    solicitud = get_object_or_404(Solicitud, id=id, usuario_solicitante=request.user)

    if not solicitud.puede_ser_editada():
        messages.error(request, 'No puedes cancelar una solicitud que ya fue procesada.')
        return redirect('usuarios:historial_solicitudes')

    if request.method == 'POST':
        solicitud.estado = 'rechazada'
        solicitud.motivo_rechazo = "Cancelada por el usuario"
        solicitud.save()

        messages.success(request, 'Solicitud cancelada con éxito.')

        # Notificar al encargado
        notificar_cancelacion_solicitud(solicitud)

        return redirect('usuarios:historial_solicitudes')

    return render(request, 'usuarios/confirmar_cancelacion.html', {'solicitud': solicitud})

def notificar_edicion_solicitud(solicitud):
    enviar_notificacion_solicitud(solicitud, "🔁 Solicitud Editada", "ha sido editada")

def notificar_cancelacion_solicitud(solicitud):
    enviar_notificacion_solicitud(solicitud, "❌ Solicitud Cancelada", "ha sido cancelada por el usuario")

def enviar_notificacion_solicitud(solicitud, titulo, accion):
    try:
        encargado = None
        if solicitud.tipo_espacio == 'carrera' and solicitud.espacio:
            encargado = solicitud.espacio.encargado
        elif solicitud.tipo_espacio == 'campus' and solicitud.espacio_campus:
            encargado = solicitud.espacio_campus.encargado

        if not encargado or not encargado.email:
            return

        subject = f'{titulo} - Sistema UABJB'
        message = f'''Estimado/a {encargado.first_name or encargado.username},

La solicitud "{solicitud.nombre_evento}" {accion}.

👤 Solicitante: {solicitud.usuario_solicitante.get_full_name() or solicitud.usuario_solicitante.username}
📅 Fecha del evento: {solicitud.fecha_evento.strftime("%d/%m/%Y %H:%M")}
📍 Espacio: {solicitud.get_nombre_espacio()}

Por favor, revisa tu dashboard para más detalles.

Saludos,
Sistema de Gestión UABJB'''

        send_mail(subject, message, 'cibanezsanguino@gmail.com', [encargado.email], fail_silently=True)
    except Exception as e:
        print(f'❌ Error enviando notificación: {str(e)}')

from django.template.loader import render_to_string

def notificar_confirmacion_solicitud(solicitud, request):
    try:
        user = solicitud.usuario_solicitante
        if not user.email:
            print("⚠️ El usuario no tiene email configurado")
            return False

        protocol = 'https' if request.is_secure() else 'http'
        domain = request.get_host()
        enlace_estado = f"{protocol}://{domain}/usuarios/historial-solicitudes/"

        # 🔧 FIX: Manejar fecha_evento que puede ser string o datetime
        if isinstance(solicitud.fecha_evento, str):
            # Si es string, intentar parsearlo
            try:
                fecha_obj = parse_datetime(solicitud.fecha_evento)
                if fecha_obj:
                    fecha_evento = fecha_obj.strftime("%d/%m/%Y a las %H:%M")
                else:
                    fecha_evento = solicitud.fecha_evento  # Usar el string tal cual
            except:
                fecha_evento = solicitud.fecha_evento
        else:
            # Si ya es datetime, formatearlo
            fecha_evento = solicitud.fecha_evento.strftime("%d/%m/%Y a las %H:%M")
        
        espacio_nombre = solicitud.get_nombre_espacio()
        tiene_archivo = bool(solicitud.archivo_adjunto)

        html_message = render_to_string('usuarios/confirmacion_solicitud.html', {
            'solicitud': solicitud,
            'user': user,
            'enlace_estado': enlace_estado,
            'fecha_evento': fecha_evento,
            'espacio_nombre': espacio_nombre,
            'tiene_archivo': tiene_archivo,
        })

        subject = "✅ Solicitud recibida - Sistema UABJB"

        send_mail(
            subject,
            None,  # texto plano (opcional)
            settings.EMAIL_HOST_USER,
            [user.email],
            html_message=html_message,
            fail_silently=False,  # 🔧 Cambiar a False para ver errores
        )
        print(f"✅ Confirmación HTML enviada a {user.email}")
        return True
    except Exception as e:
        print(f"❌ Error enviando confirmación HTML: {str(e)}")
        import traceback
        traceback.print_exc()  # 🔧 Imprimir el error completo
        return False