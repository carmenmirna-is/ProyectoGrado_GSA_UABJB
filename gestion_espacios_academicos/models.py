from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    telefono = models.CharField(max_length=15, blank=True, null=True, help_text="Número de teléfono del usuario")
    documento = models.CharField(max_length=20, unique=True, blank=True, null=True, help_text="Cédula o número de identificación")
    facultad = models.CharField(max_length=100, blank=True, null=True, help_text="Facultad a la que pertenece el usuario")
    carrera = models.CharField(max_length=100, blank=True, null=True, help_text="Carrera del usuario")
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

    def __str__(self):
        return self.username

class Facultad(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'facultad'
        verbose_name = 'Facultad'
        verbose_name_plural = 'Facultades'
    
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
    
    def __str__(self):
        return f"{self.nombre} - {self.facultad.nombre}"

class Administrador(models.Model):
    nombre = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    correo = models.EmailField(unique=True)
    contraseña = models.CharField(max_length=255)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'administrador'
        verbose_name = 'Administrador'
        verbose_name_plural = 'Administradores'
    
    def __str__(self):
        return f"{self.nombre} {self.apellidos}"
    
    def set_password(self, raw_password):
        self.contraseña = make_password(raw_password)
    
    def check_password(self, raw_password):
        return check_password(raw_password, self.contraseña)

class Encargado(models.Model):
    nombre = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    correo = models.EmailField(unique=True)
    contraseña = models.CharField(max_length=255)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'encargado'
        verbose_name = 'Encargado'
        verbose_name_plural = 'Encargados'
    
    def __str__(self):
        return f"{self.nombre} {self.apellidos}"
    
    def set_password(self, raw_password):
        self.contraseña = make_password(raw_password)
    
    def check_password(self, raw_password):
        return check_password(raw_password, self.contraseña)

class Usuario(models.Model):
    nombre = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    contraseña = models.CharField(max_length=255)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    carrera = models.ForeignKey(Carrera, on_delete=models.RESTRICT, related_name='usuarios')
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'usuario'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return f"{self.nombre} {self.apellidos} - {self.carrera.nombre}"
    
    def set_password(self, raw_password):
        self.contraseña = make_password(raw_password)
    
    def check_password(self, raw_password):
        return check_password(raw_password, self.contraseña)

class Espacio(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    capacidad = models.IntegerField(blank=True, null=True)
    ubicacion = models.CharField(max_length=200, blank=True, null=True)
    activo = models.BooleanField(default=True)
    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE, related_name='espacios')
    encargado = models.ForeignKey(Encargado, on_delete=models.CASCADE, related_name='espacios')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'espacio'
        unique_together = ['nombre', 'carrera']
        verbose_name = 'Espacio'
        verbose_name_plural = 'Espacios'
    
    def __str__(self):
        return f"{self.nombre} - {self.carrera.nombre}"
    
class EspacioCampus(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    ubicacion = models.CharField(max_length=200, blank=True, null=True)
    capacidad = models.PositiveIntegerField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

class Solicitud(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('aceptada', 'Aceptada'),
        ('rechazada', 'Rechazada'),
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
    espacio = models.ForeignKey(Espacio, on_delete=models.CASCADE, related_name='solicitudes')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='solicitudes')
    administrador = models.ForeignKey(Administrador, on_delete=models.SET_NULL, null=True, blank=True, related_name='solicitudes_procesadas')
    
    class Meta:
        db_table = 'solicitud'
        verbose_name = 'Solicitud'
        verbose_name_plural = 'Solicitudes'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.nombre_evento} - {self.espacio.nombre} - {self.estado}"
    
    def clean(self):
        if self.fecha_evento <= timezone.now():
            raise ValidationError('La fecha del evento debe ser futura.')
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
