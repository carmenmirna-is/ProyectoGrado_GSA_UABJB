from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Count
from datetime import datetime
import io
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from gestion_espacios_academicos.models import Solicitud

@login_required
def generar_reportes(request):
    if request.method == 'GET' and any(param in request.GET for param in ['formato', 'estado', 'fecha_inicio', 'fecha_fin', 'tipo_reporte']):
        formato = request.GET.get('formato', 'pdf')
        estado = request.GET.get('estado', 'todos')
        fecha_inicio = request.GET.get('fecha_inicio')
        fecha_fin = request.GET.get('fecha_fin')
        tipo_reporte = request.GET.get('tipo_reporte', 'solicitudes')
        user = request.user

        # Solo encargados pueden generar reportes
        if user.tipo_usuario != 'encargado':
            messages.error(request, 'No tienes permiso para generar reportes.')
            return render(request, 'reportes/generar_reportes.html')

        # IDs de espacios gestionados por el usuario
        ids_carrera = user.espacios_encargados.values_list('id', flat=True)
        ids_campus = user.espacios_campus_encargados.values_list('id', flat=True)

        # Filtrar solicitudes
        solicitudes = (
            Solicitud.objects
            .select_related('usuario_solicitante', 'espacio', 'espacio_campus')
            .filter(
                Q(espacio_id__in=ids_carrera) |
                Q(espacio_campus_id__in=ids_campus)
            )
        )

        # Aplicar filtros
        if estado != 'todos':
            solicitudes = solicitudes.filter(estado=estado)
        if fecha_inicio:
            try:
                fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
                solicitudes = solicitudes.filter(fecha_evento__gte=fecha_inicio_dt)
            except ValueError:
                pass
        if fecha_fin:
            try:
                fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d')
                solicitudes = solicitudes.filter(fecha_evento__lte=fecha_fin_dt)
            except ValueError:
                pass

        # Preparar datos según el tipo de reporte
        if tipo_reporte == 'solicitudes':
            data, summary = preparar_datos_solicitudes(solicitudes)
        elif tipo_reporte == 'ocupacion':
            data, summary = preparar_datos_ocupacion(solicitudes)
        elif tipo_reporte == 'facultades':
            data, summary = preparar_datos_facultades(solicitudes)
        else:
            messages.error(request, 'Tipo de reporte no válido.')
            return render(request, 'reportes/generar_reportes.html')

        # Generar archivo según formato
        if formato == 'pdf':
            return generar_pdf(data, summary, estado, fecha_inicio, fecha_fin, tipo_reporte)
        elif formato == 'excel':
            return generar_excel_openpyxl(data, summary, estado, fecha_inicio, fecha_fin, tipo_reporte)
        elif formato == 'word':
            return generar_word(data, summary, estado, fecha_inicio, fecha_fin, tipo_reporte)
        else:
            messages.error(request, 'Formato no válido.')
            return render(request, 'reportes/generar_reportes.html')

    return render(request, 'reportes/generar_reportes.html')

def preparar_datos_solicitudes(solicitudes):
    """Preparar datos para el reporte de solicitudes"""
    data = []
    for s in solicitudes:
        espacio_nombre = s.get_nombre_espacio()
        fecha_str = s.fecha_evento.strftime('%d/%m/%Y %H:%M') if s.fecha_evento else 'Sin fecha'
        data.append([
            s.id,
            s.nombre_evento,
            fecha_str,
            s.usuario_solicitante.get_full_name() or s.usuario_solicitante.username,
            espacio_nombre,
            s.estado.title(),
            s.motivo_rechazo or 'N/A'
        ])

    # Resumen estadístico
    total_solicitudes = solicitudes.count()
    aprobadas = solicitudes.filter(estado='aprobada').count()
    rechazadas = solicitudes.filter(estado='rechazada').count()
    tasa_aprobacion = (aprobadas / total_solicitudes * 100) if total_solicitudes > 0 else 0
    tasa_rechazo = (rechazadas / total_solicitudes * 100) if total_solicitudes > 0 else 0
    motivos_rechazo = solicitudes.filter(estado='rechazada').values('motivo_rechazo').annotate(total=Count('motivo_rechazo')).order_by('-total')
    patrones_temporales = solicitudes.values('fecha_evento__hour').annotate(total=Count('id')).order_by('fecha_evento__hour')

    summary = {
        'total_solicitudes': total_solicitudes,
        'aprobadas': aprobadas,
        'rechazadas': rechazadas,
        'tasa_aprobacion': f'{tasa_aprobacion:.2f}%',
        'tasa_rechazo': f'{tasa_rechazo:.2f}%',
        'motivos_rechazo': [(m['motivo_rechazo'] or 'Sin motivo', m['total']) for m in motivos_rechazo],
        'patrones_temporales': [(f"{h['fecha_evento__hour']}:00", h['total']) for h in patrones_temporales if h['fecha_evento__hour'] is not None]
    }
    return data, summary

def preparar_datos_ocupacion(solicitudes):
    """Preparar datos para el reporte de ocupación"""
    data = solicitudes.values('espacio__nombre', 'espacio_campus__nombre').annotate(
        total=Count('id'),
        aprobadas=Count('id', filter=Q(estado='aprobada'))
    ).order_by('-total')

    formatted_data = [
        [d['espacio__nombre'] or d['espacio_campus__nombre'], d['total'], d['aprobadas'], f"{d['aprobadas']/d['total']*100:.2f}%"]
        for d in data
    ]

    # Resumen estadístico
    espacios_mas_demandados = data.order_by('-total')[:5]
    espacios_menos_demandados = data.order_by('total')[:5]
    picos_actividad = solicitudes.values('fecha_evento__date').annotate(total=Count('id')).order_by('-total')[:5]

    summary = {
        'espacios_mas_demandados': [(d['espacio__nombre'] or d['espacio_campus__nombre'], d['total']) for d in espacios_mas_demandados],
        'espacios_menos_demandados': [(d['espacio__nombre'] or d['espacio_campus__nombre'], d['total']) for d in espacios_menos_demandados],
        'picos_actividad': [(d['fecha_evento__date'].strftime('%d/%m/%Y'), d['total']) for d in picos_actividad if d['fecha_evento__date']]
    }
    return formatted_data, summary

def preparar_datos_facultades(solicitudes):
    """Preparar datos para el reporte de facultades"""
    data = solicitudes.values(
        'usuario_solicitante__facultad__nombre',
        'usuario_solicitante__carrera__nombre'
    ).annotate(
        total=Count('id'),
        aprobadas=Count('id', filter=Q(estado='aprobada'))
    ).order_by('-total')

    formatted_data = [
        [d['usuario_solicitante__facultad__nombre'], d['usuario_solicitante__carrera__nombre'], d['total'], d['aprobadas']]
        for d in data
    ]

    # Resumen estadístico
    facultades_mas_activas = data.order_by('-total')[:5]
    summary = {
        'facultades_mas_activas': [(d['usuario_solicitante__facultad__nombre'], d['total']) for d in facultades_mas_activas]
    }
    return formatted_data, summary

def generar_pdf(data, summary, estado, fecha_inicio, fecha_fin, tipo_reporte):
    """Generar reporte en formato PDF"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
    elements = []

    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=16, alignment=1, spaceAfter=20)
    subtitle_style = ParagraphStyle('CustomSubtitle', parent=styles['Heading2'], fontSize=12, spaceAfter=10)
    normal_style = styles['Normal']

    # Título
    title_text = {
        'solicitudes': 'Reporte de Solicitudes - UABJB',
        'ocupacion': 'Reporte de Ocupación de Espacios - UABJB',
        'facultades': 'Reporte de Uso por Facultades - UABJB'
    }
    elements.append(Paragraph(title_text[tipo_reporte], title_style))

    # Filtros
    filter_info = f"Estado: {estado.title()}"
    if fecha_inicio:
        filter_info += f" | Desde: {fecha_inicio}"
    if fecha_fin:
        filter_info += f" | Hasta: {fecha_fin}"
    filter_info += f" | Generado: {timezone.now().strftime('%Y-%m-%d %H:%M')}"
    elements.append(Paragraph(filter_info, normal_style))
    elements.append(Spacer(1, 20))

    # Resumen estadístico
    elements.append(Paragraph("Resumen Estadístico", subtitle_style))
    summary_data = []
    if tipo_reporte == 'solicitudes':
        summary_data = [
            ['Total Solicitudes', str(summary['total_solicitudes'])],
            ['Aprobadas', str(summary['aprobadas'])],
            ['Rechazadas', str(summary['rechazadas'])],
            ['Tasa de Aprobación', summary['tasa_aprobacion']],
            ['Tasa de Rechazo', summary['tasa_rechazo']],
        ]
        if summary['motivos_rechazo']:
            elements.append(Paragraph("Motivos de Rechazo:", normal_style))
            summary_data.extend([['Motivo', 'Total']] + summary['motivos_rechazo'])
        if summary['patrones_temporales']:
            elements.append(Paragraph("Patrones Temporales:", normal_style))
            summary_data.extend([['Hora', 'Total']] + summary['patrones_temporales'])
    elif tipo_reporte == 'ocupacion':
        summary_data = [['Espacios Más Demandados', 'Solicitudes']] + summary['espacios_mas_demandados']
        summary_data += [['Espacios Menos Demandados', 'Solicitudes']] + summary['espacios_menos_demandados']
        summary_data += [['Picos de Actividad', 'Solicitudes']] + summary['picos_actividad']
    elif tipo_reporte == 'facultades':
        summary_data = [['Facultades Más Activas', 'Solicitudes']] + summary['facultades_mas_activas']

    summary_table = Table(summary_data)
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 20))

    # Tabla de datos
    headers = {
        'solicitudes': ['ID', 'Evento', 'Fecha/Hora', 'Usuario', 'Espacio', 'Estado', 'Motivo Rechazo'],
        'ocupacion': ['Espacio', 'Total Solicitudes', 'Aprobadas', 'Tasa Aprobación'],
        'facultades': ['Facultad', 'Carrera', 'Total Solicitudes', 'Aprobadas']
    }
    table_data = [headers[tipo_reporte]] + data
    
    # Ajustar anchos de columnas según el tipo de reporte
    if tipo_reporte == 'solicitudes':
        table = Table(table_data, colWidths=[30, 100, 90, 140, 110, 70, 100])
    elif tipo_reporte == 'ocupacion':
        table = Table(table_data, colWidths=[200, 120, 120, 120])
    elif tipo_reporte == 'facultades':
        table = Table(table_data, colWidths=[150, 150, 120, 120])
    else:
        table = Table(table_data)
    
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('WORDWRAP', (0, 0), (-1, -1), True)
    ]))
    elements.append(table)
    doc.build(elements)

    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    response['Content-Disposition'] = f'attachment; filename="reporte_{tipo_reporte}_{timestamp}.pdf"'
    return response

def generar_excel_openpyxl(data, summary, estado, fecha_inicio, fecha_fin, tipo_reporte):
    """Generar reporte en formato Excel usando openpyxl"""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = tipo_reporte.capitalize()

    # Estilos
    title_font = Font(name='Arial', size=16, bold=True)
    header_font = Font(name='Arial', size=12, bold=True, color='FFFFFF')
    header_fill = PatternFill(start_color='4F81BD', end_color='4F81BD', fill_type='solid')
    center_alignment = Alignment(horizontal='center')
    border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))

    # Título
    title_text = {
        'solicitudes': 'Reporte de Solicitudes - UABJB',
        'ocupacion': 'Reporte de Ocupación de Espacios - UABJB',
        'facultades': 'Reporte de Uso por Facultades - UABJB'
    }
    ws.merge_cells('A1:G1')
    title_cell = ws['A1']
    title_cell.value = title_text[tipo_reporte]
    title_cell.font = title_font
    title_cell.alignment = center_alignment

    # Filtros
    filter_info = f"Estado: {estado.title()}"
    if fecha_inicio:
        filter_info += f" | Desde: {fecha_inicio}"
    if fecha_fin:
        filter_info += f" | Hasta: {fecha_fin}"
    filter_info += f" | Generado: {timezone.now().strftime('%Y-%m-%d %H:%M')}"
    ws.merge_cells('A2:G2')
    filter_cell = ws['A2']
    filter_cell.value = filter_info
    filter_cell.alignment = center_alignment

    # Resumen estadístico
    row_start = 4
    ws.cell(row=row_start, column=1).value = "Resumen Estadístico"
    ws.cell(row=row_start, column=1).font = Font(bold=True)
    row_start += 1

    if tipo_reporte == 'solicitudes':
        summary_data = [
            ['Total Solicitudes', summary['total_solicitudes']],
            ['Aprobadas', summary['aprobadas']],
            ['Rechazadas', summary['rechazadas']],
            ['Tasa de Aprobación', summary['tasa_aprobacion']],
            ['Tasa de Rechazo', summary['tasa_rechazo']],
        ]
        if summary['motivos_rechazo']:
            summary_data.append(['Motivos de Rechazo', ''])
            summary_data.extend(summary['motivos_rechazo'])
        if summary['patrones_temporales']:
            summary_data.append(['Patrones Temporales', ''])
            summary_data.extend(summary['patrones_temporales'])
    elif tipo_reporte == 'ocupacion':
        summary_data = [['Espacios Más Demandados', 'Solicitudes']] + summary['espacios_mas_demandados']
        summary_data += [['Espacios Menos Demandados', 'Solicitudes']] + summary['espacios_menos_demandados']
        summary_data += [['Picos de Actividad', 'Solicitudes']] + summary['picos_actividad']
    elif tipo_reporte == 'facultades':
        summary_data = [['Facultades Más Activas', 'Solicitudes']] + summary['facultades_mas_activas']

    for i, row_data in enumerate(summary_data, row_start):
        for j, value in enumerate(row_data, 1):
            cell = ws.cell(row=i, column=j)
            cell.value = value
            cell.border = border
            if j == 1:
                cell.font = Font(bold=True)
        row_start += 1

    # Tabla de datos
    row_start += 2
    headers = {
        'solicitudes': ['ID', 'Evento', 'Fecha/Hora', 'Usuario', 'Espacio', 'Estado', 'Motivo Rechazo'],
        'ocupacion': ['Espacio', 'Total Solicitudes', 'Aprobadas', 'Tasa Aprobación'],
        'facultades': ['Facultad', 'Carrera', 'Total Solicitudes', 'Aprobadas']
    }
    for col_num, header in enumerate(headers[tipo_reporte], 1):
        cell = ws.cell(row=row_start, column=col_num)
        cell.value = header
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center_alignment
        cell.border = border

    for row_num, row_data in enumerate(data, row_start + 1):
        for col_num, value in enumerate(row_data, 1):
            cell = ws.cell(row=row_num, column=col_num)
            cell.value = value
            cell.alignment = center_alignment
            cell.border = border

    # Ajustar ancho de columnas
    column_widths = {
        'solicitudes': [10, 30, 20, 20, 20, 15, 25],
        'ocupacion': [30, 15, 15, 15],
        'facultades': [20, 20, 15, 15]
    }
    for col_num, width in enumerate(column_widths[tipo_reporte], 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(col_num)].width = width

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    response['Content-Disposition'] = f'attachment; filename="reporte_{tipo_reporte}_{timestamp}.xlsx"'
    return response

def generar_word(data, summary, estado, fecha_inicio, fecha_fin, tipo_reporte):
    """Generar reporte en formato Word"""
    doc = Document()
    
    # Configurar márgenes y orientación horizontal
    sections = doc.sections
    for section in sections:
        section.page_width = Inches(11)
        section.page_height = Inches(8.5)
        section.left_margin = Inches(0.5)
        section.right_margin = Inches(0.5)
    
    # Título
    title_text = {
        'solicitudes': 'Reporte de Solicitudes - UABJB',
        'ocupacion': 'Reporte de Ocupación de Espacios - UABJB',
        'facultades': 'Reporte de Uso por Facultades - UABJB'
    }
    title = doc.add_heading(title_text[tipo_reporte], level=1)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Filtros
    filter_info = f"Estado: {estado.title()}"
    if fecha_inicio:
        filter_info += f" | Desde: {fecha_inicio}"
    if fecha_fin:
        filter_info += f" | Hasta: {fecha_fin}"
    filter_info += f" | Generado: {timezone.now().strftime('%Y-%m-%d %H:%M')}"
    filter_paragraph = doc.add_paragraph(filter_info)
    filter_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    doc.add_paragraph()  # Espacio
    
    # Resumen Estadístico
    doc.add_heading('Resumen Estadístico', level=2)
    
    if tipo_reporte == 'solicitudes':
        summary_data = [
            ['Total Solicitudes', str(summary['total_solicitudes'])],
            ['Aprobadas', str(summary['aprobadas'])],
            ['Rechazadas', str(summary['rechazadas'])],
            ['Tasa de Aprobación', summary['tasa_aprobacion']],
            ['Tasa de Rechazo', summary['tasa_rechazo']],
        ]
        
        # Tabla de resumen
        table = doc.add_table(rows=len(summary_data), cols=2)
        table.style = 'Light Grid Accent 1'
        
        for i, (label, value) in enumerate(summary_data):
            table.rows[i].cells[0].text = label
            table.rows[i].cells[1].text = str(value)
        
        # Motivos de rechazo
        if summary['motivos_rechazo']:
            doc.add_paragraph()
            doc.add_heading('Motivos de Rechazo:', level=3)
            motivos_table = doc.add_table(rows=len(summary['motivos_rechazo']) + 1, cols=2)
            motivos_table.style = 'Light Grid Accent 1'
            motivos_table.rows[0].cells[0].text = 'Motivo'
            motivos_table.rows[0].cells[1].text = 'Total'
            for i, (motivo, total) in enumerate(summary['motivos_rechazo'], 1):
                motivos_table.rows[i].cells[0].text = str(motivo)
                motivos_table.rows[i].cells[1].text = str(total)
        
        # Patrones temporales
        if summary['patrones_temporales']:
            doc.add_paragraph()
            doc.add_heading('Patrones Temporales:', level=3)
            patrones_table = doc.add_table(rows=len(summary['patrones_temporales']) + 1, cols=2)
            patrones_table.style = 'Light Grid Accent 1'
            patrones_table.rows[0].cells[0].text = 'Hora'
            patrones_table.rows[0].cells[1].text = 'Total'
            for i, (hora, total) in enumerate(summary['patrones_temporales'], 1):
                patrones_table.rows[i].cells[0].text = str(hora)
                patrones_table.rows[i].cells[1].text = str(total)
    
    elif tipo_reporte == 'ocupacion':
        # Espacios más demandados
        doc.add_heading('Espacios Más Demandados:', level=3)
        table = doc.add_table(rows=len(summary['espacios_mas_demandados']) + 1, cols=2)
        table.style = 'Light Grid Accent 1'
        table.rows[0].cells[0].text = 'Espacio'
        table.rows[0].cells[1].text = 'Solicitudes'
        for i, (espacio, total) in enumerate(summary['espacios_mas_demandados'], 1):
            table.rows[i].cells[0].text = str(espacio)
            table.rows[i].cells[1].text = str(total)
        
        # Espacios menos demandados
        doc.add_paragraph()
        doc.add_heading('Espacios Menos Demandados:', level=3)
        table2 = doc.add_table(rows=len(summary['espacios_menos_demandados']) + 1, cols=2)
        table2.style = 'Light Grid Accent 1'
        table2.rows[0].cells[0].text = 'Espacio'
        table2.rows[0].cells[1].text = 'Solicitudes'
        for i, (espacio, total) in enumerate(summary['espacios_menos_demandados'], 1):
            table2.rows[i].cells[0].text = str(espacio)
            table2.rows[i].cells[1].text = str(total)
        
        # Picos de actividad
        doc.add_paragraph()
        doc.add_heading('Picos de Actividad:', level=3)
        table3 = doc.add_table(rows=len(summary['picos_actividad']) + 1, cols=2)
        table3.style = 'Light Grid Accent 1'
        table3.rows[0].cells[0].text = 'Fecha'
        table3.rows[0].cells[1].text = 'Solicitudes'
        for i, (fecha, total) in enumerate(summary['picos_actividad'], 1):
            table3.rows[i].cells[0].text = str(fecha)
            table3.rows[i].cells[1].text = str(total)
    
    elif tipo_reporte == 'facultades':
        doc.add_heading('Facultades Más Activas:', level=3)
        table = doc.add_table(rows=len(summary['facultades_mas_activas']) + 1, cols=2)
        table.style = 'Light Grid Accent 1'
        table.rows[0].cells[0].text = 'Facultad'
        table.rows[0].cells[1].text = 'Solicitudes'
        for i, (facultad, total) in enumerate(summary['facultades_mas_activas'], 1):
            table.rows[i].cells[0].text = str(facultad)
            table.rows[i].cells[1].text = str(total)
    
    doc.add_paragraph()  # Espacio
    
    # Tabla de datos principales
    doc.add_heading('Datos Detallados', level=2)
    
    headers = {
        'solicitudes': ['ID', 'Evento', 'Fecha/Hora', 'Usuario', 'Espacio', 'Estado', 'Motivo Rechazo'],
        'ocupacion': ['Espacio', 'Total Solicitudes', 'Aprobadas', 'Tasa Aprobación'],
        'facultades': ['Facultad', 'Carrera', 'Total Solicitudes', 'Aprobadas']
    }
    
    table = doc.add_table(rows=len(data) + 1, cols=len(headers[tipo_reporte]))
    table.style = 'Light Grid Accent 1'
    
    # Encabezados
    for i, header in enumerate(headers[tipo_reporte]):
        table.rows[0].cells[i].text = header
        # Hacer encabezados en negrita
        for paragraph in table.rows[0].cells[i].paragraphs:
            for run in paragraph.runs:
                run.font.bold = True
    
    # Datos
    for row_idx, row_data in enumerate(data, 1):
        for col_idx, value in enumerate(row_data):
            table.rows[row_idx].cells[col_idx].text = str(value)
    
    # Guardar en buffer
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    
    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    response['Content-Disposition'] = f'attachment; filename="reporte_{tipo_reporte}_{timestamp}.docx"'
    return response