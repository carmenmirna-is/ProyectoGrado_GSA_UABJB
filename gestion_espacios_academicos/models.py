from datetime import datetime
import os
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    telefono = models.CharField(max_length=15, blank=True, null=True, help_text="Número de teléfono del usuario")
    documento = models.CharField(max_length=20, unique=True, blank=True, null=True, help_text="Cédula o número de identificación")
    
    # Relación con facultad y carrera
    facultad = models.ForeignKey('Facultad', on_delete=models.SET_NULL, null=True, blank=True, 
                                related_name='usuarios', help_text="Facultad a la que pertenece el usuario")
    carrera = models.ForeignKey('Carrera', on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='usuarios', help_text="Carrera del usuario")
    
    tipo_usuario = models.CharField(
        max_length=20,
        choices=[
            ('administrador', 'Administrador'),
            ('encargado', 'Encargado'),
            ('usuario', 'Usuario')
        ],
        default='usuario',
        help_text="Rol del usuario en el sistema"
    )
    
    # Campos adicionales
    activo = models.BooleanField(default=True, help_text="Indica si el usuario está activo")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    token_verificacion = models.CharField(max_length=100, blank=True, null=True)
    token_expira = models.DateTimeField(blank=True, null=True)
    verificado = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.username}) - {self.get_tipo_usuario_display()}"
    
    def is_administrador(self):
        return self.tipo_usuario == 'administrador'
    
    def is_encargado(self):
        return self.tipo_usuario == 'encargado'
    
    def is_usuario_regular(self):
        return self.tipo_usuario == 'usuario'

class Facultad(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'facultad'
        verbose_name = 'Facultad'
        verbose_name_plural = 'Facultades'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre

class Carrera(models.Model):
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=20, unique=True, blank=True, null=True)
    facultad = models.ForeignKey(Facultad, on_delete=models.CASCADE, related_name='carreras')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'carrera'
        unique_together = ['nombre', 'facultad']
        verbose_name = 'Carrera'
        verbose_name_plural = 'Carreras'
        ordering = ['facultad__nombre', 'nombre']
    
    def __str__(self):
        return f"{self.nombre} - {self.facultad.nombre}"

class Espacio(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    capacidad = models.IntegerField(blank=True, null=True)
    ubicacion = models.CharField(max_length=200, blank=True, null=True)
    activo = models.BooleanField(default=True)
    
    # Relaciones actualizadas a CustomUser
    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE, related_name='espacios')
    encargado = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='espacios_encargados',
        limit_choices_to={'tipo_usuario': 'encargado'},
        help_text="Usuario encargado del espacio"
    )
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'espacio'
        unique_together = ['nombre', 'carrera']
        verbose_name = 'Espacio'
        verbose_name_plural = 'Espacios'
        ordering = ['carrera__facultad__nombre', 'carrera__nombre', 'nombre']
    
    def __str__(self):
        return f"{self.nombre} - {self.carrera.nombre}"
    
    def clean(self):
        if self.encargado and not self.encargado.is_encargado():
            raise ValidationError('El usuario asignado debe ser de tipo "encargado".')

class EspacioCampus(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    ubicacion = models.CharField(max_length=200, blank=True, null=True)
    capacidad = models.PositiveIntegerField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    # Opcional: también puede tener un encargado
    encargado = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='espacios_campus_encargados',
        limit_choices_to={'tipo_usuario': 'encargado'}
    )
    
    # 🆕 NUEVO CAMPO PARA DOCUMENTO
    documento_condiciones = models.FileField(
        upload_to='condiciones_espacios/',
        blank=True,
        null=True,
        verbose_name='Documento de Condiciones de Uso',
        help_text='Sube el PDF con las condiciones de uso del espacio'
    )

    class Meta:
        verbose_name = 'Espacio de Campus'
        verbose_name_plural = 'Espacios de Campus'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class Solicitud(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('aceptada', 'Aceptada'),
        ('rechazada', 'Rechazada'),
        ('cancelada', 'Cancelada'),
    ]

    TIPOS_ESPACIO = [
        ('carrera', 'Espacio de Carrera'),
        ('campus', 'Espacio de Campus'),
    ]
   
    nombre_evento = models.CharField(max_length=100)
    descripcion_evento = models.TextField(blank=True, null=True)
    fecha_evento = models.DateTimeField()
    fecha_fin_evento = models.DateTimeField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    motivo_rechazo = models.TextField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    archivo_adjunto = models.FileField(upload_to='solicitudes/')
    eliminada = models.BooleanField(default=False)
    fecha_eliminacion = models.DateTimeField(null=True, blank=True)
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    acepta_condiciones_uso = models.BooleanField(default=False)
    fecha_aceptacion_terminos = models.DateTimeField(null=True, blank=True)
    ip_aceptacion = models.GenericIPAddressField(null=True, blank=True)

    # Campo para determinar el tipo de espacio
    tipo_espacio = models.CharField(
        max_length=20,
        choices=TIPOS_ESPACIO,
        default='carrera',
        help_text="Tipo de espacio solicitado"
    )
    
    # Archivo adjunto
    archivo_adjunto = models.FileField(
        upload_to='solicitudes/%Y/%m/',
        blank=True,
        null=True,
        help_text="Archivo adjunto (PDF, imagen, etc.)"
    )
   
    # Relaciones - hacemos espacio nullable para manejar espacios de campus
    espacio = models.ForeignKey(
        Espacio, 
        on_delete=models.CASCADE, 
        related_name='solicitudes',
        null=True,  # Permitimos null
        blank=True,  # Permitimos blank
        help_text="Espacio de carrera (si aplica)"
    )
    
    espacio_campus = models.ForeignKey(
        EspacioCampus,
        on_delete=models.CASCADE,
        related_name='solicitudes',
        null=True,
        blank=True,
        help_text="Espacio de campus (si aplica)"
    )
    
    usuario_solicitante = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='solicitudes_realizadas',
        limit_choices_to={'tipo_usuario': 'usuario'},
        help_text="Usuario que realiza la solicitud"
    )
    administrador = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='solicitudes_procesadas',
        limit_choices_to={'tipo_usuario': 'administrador'},
        help_text="Administrador que procesa la solicitud"
    )
        # ⭐ NUEVOS CAMPOS PARA CONFIRMACIÓN
    token_confirmacion = models.CharField(
        max_length=16, 
        blank=True, 
        null=True,
        help_text="Token único de confirmación"
    )
    fecha_confirmacion = models.DateTimeField(
        blank=True, 
        null=True,
        help_text="Fecha cuando se envió la confirmación"
    )
    fecha_aprobacion = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Fecha cuando el encargado aprobó la solicitud"
    )
   
    class Meta:
        db_table = 'solicitud'
        verbose_name = 'Solicitud'
        verbose_name_plural = 'Solicitudes'
        ordering = ['-fecha_creacion']
   
    def __str__(self):
        espacio_nombre = self.get_nombre_espacio()
        return f"{self.nombre_evento} - {espacio_nombre} - {self.get_estado_display()}"
    
    def get_nombre_espacio(self):
        """Retorna el nombre del espacio solicitado"""
        if self.tipo_espacio == 'carrera' and self.espacio:
            return self.espacio.nombre
        elif self.tipo_espacio == 'campus' and self.espacio_campus:
            return self.espacio_campus.nombre
        return "Sin espacio asignado"
    
    def get_espacio_objeto(self):
        """Retorna el objeto espacio correspondiente"""
        if self.tipo_espacio == 'carrera':
            return self.espacio
        elif self.tipo_espacio == 'campus':
            return self.espacio_campus
        return None
   
    def clean(self):
        # Validar que la fecha del evento sea futura
        if self.fecha_fin_evento and self.fecha_evento:
            if self.fecha_fin_evento <= self.fecha_evento:
                raise ValidationError('La fecha de fin debe ser posterior a la fecha de inicio.')
            
        # Validar que fecha_fin_evento sea posterior a fecha_evento
        # Después (protege contra None)
        if self.fecha_fin_evento and self.fecha_evento:
            if self.fecha_fin_evento <= self.fecha_evento:
                raise ValidationError('La fecha de fin debe ser posterior a la fecha de inicio.')
        
        # Validar que se asigne el espacio correspondiente según el tipo
        if self.tipo_espacio == 'carrera' and not self.espacio:
            raise ValidationError('Debe seleccionar un espacio de carrera.')
        elif self.tipo_espacio == 'campus' and not self.espacio_campus:
            raise ValidationError('Debe seleccionar un espacio de campus.')
        
        # Validar que no se asignen ambos tipos de espacio
        if self.espacio and self.espacio_campus:
            raise ValidationError('No puede asignar ambos tipos de espacio a la vez.')
       
        if self.administrador and not self.administrador.is_administrador():
            raise ValidationError('Solo un administrador puede procesar solicitudes.')
        
        # Validar archivo adjunto
        if self.archivo_adjunto:
            if self.archivo_adjunto.size > 10 * 1024 * 1024:
                raise ValidationError('El archivo no puede ser mayor a 10MB.')
            
            allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.doc', '.docx']
            file_extension = os.path.splitext(self.archivo_adjunto.name)[1].lower()
            if file_extension not in allowed_extensions:
                raise ValidationError(f'Tipo de archivo no permitido. Formatos permitidos: {", ".join(allowed_extensions)}')
   
    def save(self, *args, **kwargs):
        # Ejecutar validaciones antes de guardar
        self.clean()
        super().save(*args, **kwargs)
   
    def puede_ser_editada(self):
        return self.estado == 'pendiente'
   
    def aprobar(self, administrador, observaciones=None):
        if not administrador.is_administrador():
            raise ValidationError('Solo un administrador puede aprobar solicitudes.')
       
        self.estado = 'aceptada'
        self.administrador = administrador
        if observaciones:
            self.observaciones = observaciones
        self.save()
   
    def rechazar(self, administrador, motivo_rechazo):
        if not administrador.is_administrador():
            raise ValidationError('Solo un administrador puede rechazar solicitudes.')
       
        self.estado = 'rechazada'
        self.administrador = administrador
        self.motivo_rechazo = motivo_rechazo
        self.save()
    
    @property
    def nombre_archivo(self):
        if self.archivo_adjunto:
            return os.path.basename(self.archivo_adjunto.name)
        return None
    
    @property
    def tamano_archivo_legible(self):
        if self.archivo_adjunto:
            size = self.archivo_adjunto.size
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
        return None

# Modelo adicional para historiales de solicitudes (opcional)
class HistorialSolicitud(models.Model):
    solicitud = models.ForeignKey(Solicitud, on_delete=models.CASCADE, related_name='historial')
    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    accion = models.CharField(max_length=50)  # 'creada', 'aprobada', 'rechazada', 'modificada'
    descripcion = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Historial de Solicitud'
        verbose_name_plural = 'Historiales de Solicitudes'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.solicitud.nombre_evento} - {self.accion} - {self.fecha}"