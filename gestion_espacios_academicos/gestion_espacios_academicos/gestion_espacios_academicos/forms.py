import os
from datetime import datetime, timedelta
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Facultad, Carrera, Espacio, CustomUser, EspacioCampus, Solicitud
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model
import uuid

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Usuario o correo electrónico'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'})
    )

User = get_user_model()

class CustomRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}))
    last_name = forms.CharField(max_length=30, required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}))
    email = forms.EmailField(required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'}))
    telefono = forms.CharField(max_length=15, required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'}))
    documento = forms.CharField(max_length=20, required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cédula/CI'}))

    carrera = forms.ModelChoiceField(
        queryset=Carrera.objects.all(),
        empty_label="Seleccionar Carrera",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña'
        }),
        help_text='Tu contraseña debe tener al menos 8 caracteres.'
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña'
        }),
        help_text='Ingresa la misma contraseña para verificación.'
    )

    class Meta:
        model = User
        fields = (
            'username', 'first_name', 'last_name', 'email',
            'telefono', 'documento', 'carrera',
            'password1', 'password2'
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.tipo_usuario = 'usuario'
        user.facultad = self.cleaned_data['carrera'].facultad

        # ❗ Desactivar hasta verificar correo
        user.is_active = False
        user.activo = False
        user.verificado = False

        # Generar token y expiración
        user.token_verificacion = str(uuid.uuid4())
        user.token_expira = timezone.now() + timedelta(hours=24)

        if commit:
            user.save()
        return user

# Formulario para registrar y editar facultades
class FacultadForm(forms.ModelForm):
    class Meta:
        model = Facultad
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la facultad'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Descripción de la facultad'}),
        }
        labels = {
            'nombre': 'Nombre',
            'descripcion': 'Descripción',
        }

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        if not nombre.strip():
            raise ValidationError('El nombre de la facultad no puede estar vacío.')
        return nombre

# Formulario para registrar y editar carreras
class CarreraForm(forms.ModelForm):
    class Meta:
        model = Carrera
        fields = ['nombre', 'codigo', 'facultad']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la carrera'}),
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código de la carrera'}),
            'facultad': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'nombre': 'Nombre',
            'codigo': 'Código',
            'facultad': 'Facultad',
        }

    def clean(self):
        cleaned_data = super().clean()
        nombre = cleaned_data.get('nombre')
        facultad = cleaned_data.get('facultad')
        codigo = cleaned_data.get('codigo')

        # Validar que el nombre no esté vacío
        if not nombre or not nombre.strip():
            raise ValidationError('El nombre de la carrera no puede estar vacío.')

        # Validar unicidad de nombre dentro de la facultad
        if Carrera.objects.filter(nombre=nombre, facultad=facultad).exclude(pk=self.instance.pk).exists():
            raise ValidationError('Ya existe una carrera con este nombre en la facultad seleccionada.')

        # Validar que el código, si se proporciona, sea único
        if codigo and Carrera.objects.filter(codigo=codigo).exclude(pk=self.instance.pk).exists():
            raise ValidationError('El código ya está en uso por otra carrera.')

        return cleaned_data

# Formulario para registrar y editar espacios
class EspacioForm(forms.ModelForm):
    class Meta:
        model = Espacio
        fields = ['nombre', 'descripcion', 'capacidad', 'ubicacion', 'activo', 'carrera', 'encargado']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del espacio'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Descripción del espacio'}),
            'capacidad': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Capacidad'}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ubicación'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'carrera': forms.Select(attrs={'class': 'form-control'}),
            'encargado': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'nombre': 'Nombre',
            'descripcion': 'Descripción',
            'capacidad': 'Capacidad',
            'ubicacion': 'Ubicación',
            'activo': 'Activo',
            'carrera': 'Carrera',
            'encargado': 'Encargado',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar encargados para mostrar solo usuarios con tipo_usuario='encargado'
        self.fields['encargado'].queryset = CustomUser.objects.filter(tipo_usuario='encargado')
        # Hacer que carrera sea opcional (para espacios comunes)
        self.fields['carrera'].required = False

    def clean(self):
        cleaned_data = super().clean()
        nombre = cleaned_data.get('nombre')
        carrera = cleaned_data.get('carrera')

        # Validar que el nombre no esté vacío
        if not nombre or not nombre.strip():
            raise ValidationError('El nombre del espacio no puede estar vacío.')

        # Validar unicidad de nombre dentro de la carrera (o nulo para espacios comunes)
        if Espacio.objects.filter(nombre=nombre, carrera=carrera).exclude(pk=self.instance.pk).exists():
            raise ValidationError('Ya existe un espacio con este nombre para esta carrera o como espacio común.')

        # Validar que la capacidad sea positiva
        capacidad = cleaned_data.get('capacidad')
        if capacidad is not None and capacidad <= 0:
            raise ValidationError('La capacidad debe ser un número positivo.')

        return cleaned_data

class EspacioCampusForm(forms.ModelForm):
    class Meta:
        model = EspacioCampus
        fields = ['nombre', 'ubicacion', 'capacidad', 'descripcion', 'encargado', 'documento_condiciones']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Salón Bicentenario'}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Edificio Principal, Piso 2'}),
            'capacidad': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 100'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Descripción del espacio...'}),
            'encargado': forms.Select(attrs={'class': 'form-control'}),
            'documento_condiciones': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf',  # Solo acepta PDFs
            }),
        }
        labels = {
            'nombre': 'Nombre del Espacio',
            'ubicacion': 'Ubicación',
            'capacidad': 'Capacidad (personas)',
            'descripcion': 'Descripción',
            'encargado': 'Encargado',
            'documento_condiciones': '📄 Documento de Condiciones de Uso (PDF)',
        }
        help_texts = {
            'documento_condiciones': 'Sube el PDF con las condiciones y normas de uso del espacio',
        }

# Formulario para registrar y editar encargados
class EncargadoRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}), required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmar contraseña'}), required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'telefono', 'documento']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombres'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellidos'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'}),
            'documento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cédula de identidad'}),
        }
        labels = {
            'username': 'Nombre de usuario',
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
            'email': 'Correo electrónico',
            'telefono': 'Teléfono',
            'documento': 'Cédula de identidad',
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        documento = cleaned_data.get('documento')

        # Validar que las contraseñas coincidan
        if password and confirm_password and password != confirm_password:
            raise ValidationError('Las contraseñas no coinciden.')

        # Validar unicidad del nombre de usuario
        if CustomUser.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise ValidationError('El nombre de usuario ya está en uso.')

        # Validar unicidad del correo electrónico
        if email and CustomUser.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError('El correo electrónico ya está en uso.')

        # Validar unicidad de la cédula
        if documento and CustomUser.objects.filter(documento=documento).exclude(pk=self.instance.pk).exists():
            raise ValidationError('La cédula de identidad ya está registrada.')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class SolicitudRechazoForm(forms.ModelForm):
    class Meta:
        model = Solicitud
        fields = ['motivo_rechazo']
        widgets = {
            'motivo_rechazo': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Especifica el motivo del rechazo'}),
        }

class SolicitudForm(forms.ModelForm):
    TIPO_ESPACIO_CHOICES = [
        ('', 'Selecciona el tipo de espacio'),
        ('carrera', 'Espacio de Carrera'),
        ('campus', 'Espacio de Campus'),
    ]

    tipo_espacio = forms.ChoiceField(
        choices=TIPO_ESPACIO_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Tipo de espacio'
    )

    espacio_carrera = forms.ModelChoiceField(
        queryset=Espacio.objects.filter(activo=True),
        empty_label="Selecciona un espacio de carrera",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Espacio de Carrera',
        to_field_name='id'  # IMPORTANTE: Forzar que use el ID
    )

    espacio_campus = forms.ModelChoiceField(
        queryset=EspacioCampus.objects.all(),
        empty_label="Selecciona un espacio de campus",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Espacio de Campus',
        to_field_name='id'  # IMPORTANTE: Forzar que use el ID
    )

    class Meta:
        model = Solicitud
        fields = [
            'nombre_evento',
            'descripcion_evento',
            'fecha_evento',
            'fecha_fin_evento',
            'tipo_espacio',
            'espacio_carrera',
            'espacio_campus',
            'archivo_adjunto',
            'observaciones'
        ]
        widgets = {
            'nombre_evento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del evento'
            }),
            'descripcion_evento': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe tu evento...'
            }),
            'fecha_evento': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'fecha_fin_evento': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'archivo_adjunto': forms.FileInput(attrs={
                'class': 'form-control-file',
                'accept': '.pdf,.jpg,.jpeg,.png,.gif,.doc,.docx',
                'style': 'display: none;'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones adicionales (opcional)...'
            })
        }

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo_espacio')
        carrera = cleaned_data.get('espacio_carrera')
        campus = cleaned_data.get('espacio_campus')
        fecha_evento = cleaned_data.get('fecha_evento')
        fecha_fin = cleaned_data.get('fecha_fin_evento')
        archivo = cleaned_data.get('archivo_adjunto')

        print(f"DEBUG CLEAN: tipo={tipo}")
        print(f"DEBUG CLEAN: carrera={carrera} (type: {type(carrera)})")
        print(f"DEBUG CLEAN: campus={campus} (type: {type(campus)})")

        # VALIDACIÓN MEJORADA de espacios
        if tipo == 'carrera':
            # Verificar que el campo carrera esté presente y no sea None
            if not carrera:
                print("ERROR: Espacio carrera no seleccionado")
                self.add_error('espacio_carrera', 'Debes seleccionar un espacio de carrera.')
            else:
                print(f"SUCCESS: Espacio carrera válido: {carrera}")
                # Limpiar el campo de campus
                cleaned_data['espacio_campus'] = None
        elif tipo == 'campus':
            # Verificar que el campo campus esté presente y no sea None
            if not campus:
                print("ERROR: Espacio campus no seleccionado")
                self.add_error('espacio_campus', 'Debes seleccionar un espacio de campus.')
            else:
                print(f"SUCCESS: Espacio campus válido: {campus}")
                # Limpiar el campo de carrera
                cleaned_data['espacio_carrera'] = None
        elif tipo:  # Si hay un tipo pero no es válido
            self.add_error('tipo_espacio', 'Debes seleccionar un tipo de espacio válido.')

        # Validar fechas
        if fecha_evento and fecha_evento <= timezone.now():
            self.add_error('fecha_evento', 'La fecha del evento debe ser futura.')

        if fecha_fin and fecha_evento and fecha_fin <= fecha_evento:
            self.add_error('fecha_fin_evento', 'La fecha de finalización debe ser posterior a la de inicio.')

        # Validar archivo
        if archivo:
            ext = os.path.splitext(archivo.name)[1].lower()
            if ext not in ['.pdf','.jpg','.jpeg','.png','.gif','.doc','.docx']:
                self.add_error('archivo_adjunto', 'Formato de archivo no permitido.')
            if archivo.size > 10 * 1024 * 1024:
                self.add_error('archivo_adjunto', 'El archivo no puede superar los 10 MB.')

        print(f"DEBUG CLEAN FINAL: Errors = {self.errors}")
        return cleaned_data