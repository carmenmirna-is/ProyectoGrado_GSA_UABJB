from django import forms
from django.core.exceptions import ValidationError
from .models import Facultad, Carrera, Espacio, CustomUser

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
            'carrera': 'Carrera (opcional, dejar en blanco para espacios comunes)',
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

# Formulario para registrar y editar encargados
class EncargadoRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}), required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmar contraseña'}), required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'telefono', 'document']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombres'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellidos'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'}),
            'document': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cédula de identidad'}),
        }
        labels = {
            'username': 'Nombre de usuario',
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
            'email': 'Correo electrónico',
            'telefono': 'Teléfono',
            'document': 'Cédula de identidad',
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        document = cleaned_data.get('document')

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
        if document and CustomUser.objects.filter(document=document).exclude(pk=self.instance.pk).exists():
            raise ValidationError('La cédula de identidad ya está registrada.')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user