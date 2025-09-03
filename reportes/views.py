# encargados/views.py  (reportes)

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
import openpyxl
from gestion_espacios_academicos.models import Solicitud
from datetime import datetime
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

@login_required
def generar_reportes(request):
    if request.method == 'GET' and any(param in request.GET for param in ['formato', 'estado', 'fecha_inicio', 'fecha_fin']):
        formato = request.GET.get('formato', 'pdf')
        estado = request.GET.get('estado', 'todos')
        fecha_inicio = request.GET.get('fecha_inicio')
        fecha_fin = request.GET.get('fecha_fin')

        user = request.user

        # Solo encargados pueden generar reportes
        if user.tipo_usuario != 'encargado':
            messages.error(request, 'No tienes permiso para generar reportes.')
            return render(request, 'reportes/generar_reportes.html')

        # IDs de espacios que gestiona
        ids_carrera = user.espacios_encargados.values_list('id', flat=True)
        ids_campus = user.espacios_campus_encargados.values_list('id', flat=True)

        # Filtrar solicitudes de sus espacios
        solicitudes = (
            Solicitud.objects
            .select_related('usuario_solicitante', 'espacio', 'espacio_campus')
            .filter(
                Q(espacio_id__in=ids_carrera) |
                Q(espacio_campus_id__in=ids_campus)
            )
        )

        # Filtrar por estado
        if estado != 'todos':
            solicitudes = solicitudes.filter(estado=estado)

        # Filtrar por rango de fechas
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

        # Preparar datos para el reporte
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
                s.estado.title()
            ])

        # Generar el archivo según formato
        if formato == 'pdf':
            return generar_pdf(data, estado, fecha_inicio, fecha_fin)
        elif formato == 'excel':
            return generar_excel_openpyxl(data, estado, fecha_inicio, fecha_fin)
        elif formato == 'word':
            return generar_word(data, estado, fecha_inicio, fecha_fin)

    # Si no hay parámetros, mostrar formulario
    return render(request, 'reportes/generar_reportes.html')

def generar_pdf(data, estado, fecha_inicio, fecha_fin):
    """Generar reporte en formato PDF"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=1,  # Center
        spaceAfter=30,
    )
    
    # Título
    title = Paragraph("Reporte de Solicitudes - UABJB", title_style)
    elements.append(title)
    
    # Información del filtro
    filter_info = f"Estado: {estado.title()}"
    if fecha_inicio:
        filter_info += f" | Desde: {fecha_inicio}"
    if fecha_fin:
        filter_info += f" | Hasta: {fecha_fin}"
    filter_info += f" | Generado: {timezone.now().strftime('%Y-%m-%d %H:%M')}"
    
    filter_para = Paragraph(filter_info, styles['Normal'])
    elements.append(filter_para)
    elements.append(Spacer(1, 20))
    
    # Tabla de datos
    table_data = [['ID', 'Evento', 'Fecha/Hora', 'Usuario', 'Espacio', 'Estado']]
    table_data.extend(data)
    
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    doc.build(elements)
    
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reporte_solicitudes_{timezone.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
    return response

def generar_excel_openpyxl(data, estado, fecha_inicio, fecha_fin):
    """Generar reporte en formato Excel usando openpyxl"""
    # Crear un nuevo workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Solicitudes"
    
    # Estilos
    title_font = Font(name='Arial', size=16, bold=True)
    header_font = Font(name='Arial', size=12, bold=True, color='FFFFFF')
    header_fill = PatternFill(start_color='4F81BD', end_color='4F81BD', fill_type='solid')
    center_alignment = Alignment(horizontal='center')
    
    # Título
    ws.merge_cells('A1:E1')
    title_cell = ws['A1']
    title_cell.value = 'Reporte de Solicitudes - UABJB'
    title_cell.font = title_font
    title_cell.alignment = center_alignment
    
    # Información del filtro
    filter_info = f"Estado: {estado.title()}"
    if fecha_inicio:
        filter_info += f" | Desde: {fecha_inicio}"
    if fecha_fin:
        filter_info += f" | Hasta: {fecha_fin}"
    filter_info += f" | Generado: {timezone.now().strftime('%Y-%m-%d %H:%M')}"
    
    ws.merge_cells('A2:E2')
    filter_cell = ws['A2']
    filter_cell.value = filter_info
    filter_cell.alignment = center_alignment
    
    # Encabezados
    headers = ['ID', 'Evento', 'Fecha/Hora', 'Usuario', 'Espacio', 'Estado']
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=4, column=col_num)
        cell.value = header
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center_alignment
    
    # Datos
    for row_num, row_data in enumerate(data, 5):
        for col_num, value in enumerate(row_data, 1):
            cell = ws.cell(row=row_num, column=col_num)
            cell.value = value
            if col_num == 1:  # ID column
                cell.alignment = center_alignment
    
    # Ajustar ancho de columnas
    column_widths = [5, 30, 20, 15, 12]
    for col_num, width in enumerate(column_widths, 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(col_num)].width = width
    
    # Guardar en buffer
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    
    response = HttpResponse(
        buffer.getvalue(), 
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="reporte_solicitudes_{timezone.now().strftime("%Y%m%d_%H%M%S")}.xlsx"'
    return response

def generar_word(data, estado, fecha_inicio, fecha_fin):
    """Generar reporte en formato Word"""
    document = Document()
    
    # Título
    title = document.add_heading('Reporte de Solicitudes - UABJB', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Información del filtro
    filter_info = f"Estado: {estado.title()}"
    if fecha_inicio:
        filter_info += f" | Desde: {fecha_inicio}"
    if fecha_fin:
        filter_info += f" | Hasta: {fecha_fin}"
    filter_info += f" | Generado: {timezone.now().strftime('%Y-%m-%d %H:%M')}"
    
    filter_para = document.add_paragraph(filter_info)
    filter_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Tabla
    table = document.add_table(rows=1, cols=5)
    table.style = 'Table Grid'
    
    # Encabezados
    headers = ['ID', 'Evento', 'Fecha/Hora', 'Usuario', 'Espacio', 'Estado']
    hdr_cells = table.rows[0].cells
    for i, header in enumerate(headers):
        hdr_cells[i].text = header
        hdr_cells[i].paragraphs[0].runs[0].bold = True
    
    # Datos
    for row_data in data:
        row_cells = table.add_row().cells
        for i, value in enumerate(row_data):
            row_cells[i].text = str(value)
    
    # Ajustar ancho de columnas
    for row in table.rows:
        row.cells[0].width = Inches(0.5)  # ID
        row.cells[1].width = Inches(2.5)  # Evento
        row.cells[2].width = Inches(1.5)  # Fecha
        row.cells[3].width = Inches(1.2)  # Usuario
        row.cells[4].width = Inches(1.0)  # Estado
    
    # Guardar en buffer
    buffer = io.BytesIO()
    document.save(buffer)
    buffer.seek(0)
    
    response = HttpResponse(
        buffer.getvalue(), 
        content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )
    response['Content-Disposition'] = f'attachment; filename="reporte_solicitudes_{timezone.now().strftime("%Y%m%d_%H%M%S")}.docx"'
    return response