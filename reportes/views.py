from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
from administrador.views import user_type_required
from .models import Solicitud  # Ajusta la importación según la app donde esté el modelo
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from openpyxl import Workbook
from docx import Document
import io
from datetime import datetime

@user_type_required('encargado')
def generar_reportes(request):
    if request.method == 'GET':
        formato = request.GET.get('formato', 'pdf')
        estado = request.GET.get('estado', 'todos')
        fecha_inicio = request.GET.get('fecha_inicio')
        fecha_fin = request.GET.get('fecha_fin')

        # Filtrar solicitudes
        solicitudes = Solicitud.objects.all()
        if estado != 'todos':
            solicitudes = solicitudes.filter(estado=estado)
        if fecha_inicio:
            solicitudes = solicitudes.filter(fecha__gte=datetime.strptime(fecha_inicio, '%Y-%m-%d'))
        if fecha_fin:
            solicitudes = solicitudes.filter(fecha__lte=datetime.strptime(fecha_fin, '%Y-%m-%d') + timezone.timedelta(days=1))

        # Preparar datos para el reporte
        data = [['ID', 'Evento', 'Fecha', 'Solicitante', 'Estado']]
        for s in solicitudes:
            data.append([s.id, s.nombre_evento, s.fecha.strftime('%Y-%m-%d %H:%M'), s.usuario.username, s.estado])

        if formato == 'pdf':
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()
            title = Paragraph("Reporte de Solicitudes - UABJB", styles['Heading1'])
            elements.append(title)
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(table)
            doc.build(elements)
            buffer.seek(0)
            response = HttpResponse(buffer, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="reporte_solicitudes_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
            return response

        elif formato == 'excel':
            wb = Workbook()
            ws = wb.active
            ws.title = "Solicitudes"
            for row in data:
                ws.append(row)
            buffer = io.BytesIO()
            wb.save(buffer)
            buffer.seek(0)
            response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="reporte_solicitudes_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx"'
            return response

        elif formato == 'word':
            doc = Document()
            doc.add_heading('Reporte de Solicitudes - UABJB', 0)
            table = doc.add_table(rows=1, cols=5)
            hdr_cells = table.rows[0].cells
            hdr_cells[0].text = 'ID'
            hdr_cells[1].text = 'Evento'
            hdr_cells[2].text = 'Fecha'
            hdr_cells[3].text = 'Solicitante'
            hdr_cells[4].text = 'Estado'
            for item in data[1:]:
                row_cells = table.add_row().cells
                row_cells[0].text = str(item[0])
                row_cells[1].text = item[1]
                row_cells[2].text = item[2]
                row_cells[3].text = item[3]
                row_cells[4].text = item[4]
            buffer = io.BytesIO()
            doc.save(buffer)
            buffer.seek(0)
            response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            response['Content-Disposition'] = f'attachment; filename="reporte_solicitudes_{datetime.now().strftime("%Y%m%d_%H%M%S")}.docx"'
            return response

    context = {
        'formato': 'pdf',  # Valor por defecto para el formulario
        'estado': 'todos',
    }
    return render(request, 'reportes/generar_reportes.html', context)
# Create your views here.