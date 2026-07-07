from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Facultad, Carrera, Espacio, EspacioCampus, Solicitud, CustomUser

# Registro del CustomUser
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # Campos que se mostrarán en la lista
    list_display = (
        'username', 
        'email', 
        'first_name', 
        'last_name', 
        'tipo_usuario',
        'facultad',
        'carrera',
        'is_active',
        'date_joined'
    )
    
    # Filtros laterales
    list_filter = (
        'tipo_usuario',
        'is_active',
        'is_staff',
        'is_superuser',
        'facultad',
        'carrera',
        'date_joined'
    )
    
    # Campos de búsqueda
    search_fields = (
        'username',
        'first_name',
        'last_name',
        'email',
        'documento',
        'telefono'
    )
    
    # Ordenamiento
    ordering = ('username',)
    
    # Configuración de fieldsets para el formulario de edición
    fieldsets = UserAdmin.fieldsets + (
        ('Información Adicional', {
            'fields': ('telefono', 'documento', 'tipo_usuario')
        }),
        ('Relaciones Académicas', {
            'fields': ('facultad', 'carrera')
        }),
        ('Estado', {
            'fields': ('activo',)
        })
    )
    
    # Campos para el formulario de agregar usuario
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información Adicional', {
            'fields': ('email', 'first_name', 'last_name', 'telefono', 'documento', 'tipo_usuario')
        }),
        ('Relaciones Académicas', {
            'fields': ('facultad', 'carrera')
        }),
    )
    
    # Optimizar consultas
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('facultad', 'carrera')
    
    # Personalizar el campo facultad en la lista
    def get_facultad_display(self, obj):
        return obj.facultad.nombre if obj.facultad else '-'
    get_facultad_display.short_description = 'Facultad'
    get_facultad_display.admin_order_field = 'facultad__nombre'
    
    # Personalizar el campo carrera en la lista
    def get_carrera_display(self, obj):
        return obj.carrera.nombre if obj.carrera else '-'
    get_carrera_display.short_description = 'Carrera'
    get_carrera_display.admin_order_field = 'carrera__nombre'

@admin.register(Facultad)
class FacultadAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion', 'fecha_creacion')
    search_fields = ('nombre',)
    ordering = ('nombre',)

@admin.register(Carrera)
class CarreraAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'facultad', 'fecha_creacion')
    list_filter = ('facultad',)
    search_fields = ('nombre', 'facultad__nombre')
    ordering = ('facultad__nombre', 'nombre')

@admin.register(Espacio)
class EspacioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'carrera', 'capacidad', 'ubicacion', 'encargado', 'activo')
    list_filter = ('activo', 'carrera__facultad', 'carrera')
    search_fields = ('nombre', 'carrera__nombre', 'ubicacion')
    ordering = ('carrera__facultad__nombre', 'carrera__nombre', 'nombre')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'descripcion', 'capacidad', 'ubicacion', 'activo')
        }),
        ('Relaciones', {
            'fields': ('carrera', 'encargado')
        }),
    )

@admin.register(EspacioCampus)
class EspacioCampusAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'ubicacion', 'capacidad', 'encargado', 'fecha_creacion')
    search_fields = ('nombre', 'ubicacion')
    ordering = ('nombre',)
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'descripcion', 'ubicacion', 'capacidad')
        }),
        ('Administración', {
            'fields': ('encargado',)
        }),
    )

@admin.register(Solicitud)
class SolicitudAdmin(admin.ModelAdmin):
    list_display = (
        'nombre_evento', 
        'get_espacio_display', 
        'tipo_espacio',
        'usuario_solicitante', 
        'fecha_evento',
        'estado',
        'fecha_creacion',
        'archivo_adjunto_link'
    )
    list_filter = (
        'estado', 
        'tipo_espacio',
        'fecha_creacion', 
        'fecha_evento',
        'espacio__carrera__facultad'
    )
    search_fields = (
        'nombre_evento', 
        'usuario_solicitante__username',
        'usuario_solicitante__first_name',
        'usuario_solicitante__last_name',
        'espacio__nombre',
        'espacio_campus__nombre'
    )
    ordering = ('-fecha_creacion',)
    
    fieldsets = (
        ('Información del Evento', {
            'fields': ('nombre_evento', 'descripcion_evento', 'fecha_evento', 'fecha_fin_evento')
        }),
        ('Espacio Solicitado', {
            'fields': ('tipo_espacio', 'espacio', 'espacio_campus'),
            'description': 'Seleccione el tipo de espacio y luego el espacio específico.'
        }),
        ('Solicitante', {
            'fields': ('usuario_solicitante',)
        }),
        ('Estado y Procesamiento', {
            'fields': ('estado', 'administrador', 'motivo_rechazo', 'observaciones')
        }),
        ('Archivo Adjunto', {
            'fields': ('archivo_adjunto',)
        }),
        ('Metadatos', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    
    def get_espacio_display(self, obj):
        """Muestra el espacio correspondiente según el tipo"""
        if obj.tipo_espacio == 'carrera' and obj.espacio:
            return format_html(
                '<span style="color: #2196F3;"><i class="fas fa-graduation-cap"></i> {}</span>',
                obj.espacio.nombre
            )
        elif obj.tipo_espacio == 'campus' and obj.espacio_campus:
            return format_html(
                '<span style="color: #4CAF50;"><i class="fas fa-university"></i> {}</span>',
                obj.espacio_campus.nombre
            )
        return format_html('<span style="color: #f44336;">Sin espacio asignado</span>')
    get_espacio_display.short_description = 'Espacio'
    get_espacio_display.admin_order_field = 'espacio__nombre'
    
    def archivo_adjunto_link(self, obj):
        """Crea un enlace para descargar el archivo adjunto"""
        if obj.archivo_adjunto:
            return format_html(
                '<a href="{}" target="_blank"><i class="fas fa-download"></i> {}</a>',
                obj.archivo_adjunto.url,
                obj.nombre_archivo
            )
        return format_html('<span style="color: #999;">Sin archivo</span>')
    archivo_adjunto_link.short_description = 'Archivo'
    
    def get_queryset(self, request):
        """Optimizar consultas"""
        return super().get_queryset(request).select_related(
            'usuario_solicitante',
            'administrador',
            'espacio__carrera__facultad',
            'espacio_campus'
        )
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Personalizar los campos de selección"""
        if db_field.name == "espacio":
            kwargs["queryset"] = Espacio.objects.filter(activo=True).select_related('carrera')
        elif db_field.name == "usuario_solicitante":
            kwargs["queryset"] = CustomUser.objects.filter(tipo_usuario='usuario')
        elif db_field.name == "administrador":
            kwargs["queryset"] = CustomUser.objects.filter(tipo_usuario='administrador')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    actions = ['aprobar_solicitudes', 'rechazar_solicitudes']
    
    def aprobar_solicitudes(self, request, queryset):
        """Acción para aprobar solicitudes masivamente"""
        count = 0
        for solicitud in queryset.filter(estado='pendiente'):
            try:
                solicitud.aprobar(request.user, "Aprobada mediante acción masiva")
                count += 1
            except Exception as e:
                self.message_user(
                    request, 
                    f'Error al aprobar solicitud {solicitud.id}: {str(e)}',
                    level='ERROR'
                )
        
        if count > 0:
            self.message_user(
                request,
                f'Se aprobaron {count} solicitudes correctamente.',
                level='SUCCESS'
            )
    aprobar_solicitudes.short_description = "Aprobar solicitudes seleccionadas"
    
    def rechazar_solicitudes(self, request, queryset):
        """Acción para rechazar solicitudes masivamente"""
        count = 0
        for solicitud in queryset.filter(estado='pendiente'):
            try:
                solicitud.rechazar(request.user, "Rechazada mediante acción masiva")
                count += 1
            except Exception as e:
                self.message_user(
                    request,
                    f'Error al rechazar solicitud {solicitud.id}: {str(e)}',
                    level='ERROR'
                )
        
        if count > 0:
            self.message_user(
                request,
                f'Se rechazaron {count} solicitudes correctamente.',
                level='SUCCESS'
            )
    rechazar_solicitudes.short_description = "Rechazar solicitudes seleccionadas"

# Registro del modelo HistorialSolicitud (si lo estás usando)
# Descomenta las siguientes líneas si quieres administrar el historial desde el admin
"""
@admin.register(HistorialSolicitud)
class HistorialSolicitudAdmin(admin.ModelAdmin):
    list_display = ('solicitud', 'usuario', 'accion', 'fecha')
    list_filter = ('accion', 'fecha')
    search_fields = ('solicitud__nombre_evento', 'usuario__username', 'descripcion')
    ordering = ('-fecha',)
    readonly_fields = ('fecha',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('solicitud', 'usuario')
"""

# Personalización adicional del admin
admin.site.site_header = "Administración UABJB"
admin.site.site_title = "UABJB Admin"
admin.site.index_title = "Panel de Administración"