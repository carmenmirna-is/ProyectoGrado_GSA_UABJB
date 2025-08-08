from django.contrib import admin
from django import forms
from django.contrib.auth.hashers import make_password
from .models import Facultad, Carrera, Administrador, Encargado, Usuario, Espacio, Solicitud

# Formulario personalizado para Administrador
class AdministradorForm(forms.ModelForm):
    contraseña = forms.CharField(
        widget=forms.PasswordInput(),
        help_text="Ingresa la contraseña para el administrador"
    )
    confirmar_contraseña = forms.CharField(
        widget=forms.PasswordInput(),
        help_text="Confirma la contraseña"
    )
    
    class Meta:
        model = Administrador
        fields = '__all__'
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('contraseña')
        confirm_password = cleaned_data.get('confirmar_contraseña')
        
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Las contraseñas no coinciden")
        
        return cleaned_data
    
    def save(self, commit=True):
        admin = super().save(commit=False)
        if self.cleaned_data.get('contraseña'):
            admin.set_password(self.cleaned_data['contraseña'])
        if commit:
            admin.save()
        return admin

# Formulario personalizado para Encargado
class EncargadoForm(forms.ModelForm):
    contraseña = forms.CharField(
        widget=forms.PasswordInput(),
        help_text="Ingresa la contraseña para el encargado"
    )
    confirmar_contraseña = forms.CharField(
        widget=forms.PasswordInput(),
        help_text="Confirma la contraseña"
    )
    
    class Meta:
        model = Encargado
        fields = '__all__'
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('contraseña')
        confirm_password = cleaned_data.get('confirmar_contraseña')
        
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Las contraseñas no coinciden")
        
        return cleaned_data
    
    def save(self, commit=True):
        encargado = super().save(commit=False)
        if self.cleaned_data.get('contraseña'):
            encargado.set_password(self.cleaned_data['contraseña'])
        if commit:
            encargado.save()
        return encargado

# Formulario personalizado para Usuario
class UsuarioForm(forms.ModelForm):
    contraseña = forms.CharField(
        widget=forms.PasswordInput(),
        help_text="Ingresa la contraseña para el usuario"
    )
    confirmar_contraseña = forms.CharField(
        widget=forms.PasswordInput(),
        help_text="Confirma la contraseña"
    )
    
    class Meta:
        model = Usuario
        fields = '__all__'
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('contraseña')
        confirm_password = cleaned_data.get('confirmar_contraseña')
        
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Las contraseñas no coinciden")
        
        return cleaned_data
    
    def save(self, commit=True):
        usuario = super().save(commit=False)
        if self.cleaned_data.get('contraseña'):
            usuario.set_password(self.cleaned_data['contraseña'])
        if commit:
            usuario.save()
        return usuario

# Registro de modelos con formularios personalizados
@admin.register(Facultad)
class FacultadAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'fecha_creacion']
    search_fields = ['nombre']
    readonly_fields = ['fecha_creacion']

@admin.register(Carrera)
class CarreraAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'codigo', 'facultad', 'fecha_creacion']
    search_fields = ['nombre', 'codigo']
    list_filter = ['facultad']
    readonly_fields = ['fecha_creacion']

@admin.register(Administrador)
class AdministradorAdmin(admin.ModelAdmin):
    form = AdministradorForm
    list_display = ['nombre', 'apellidos', 'correo', 'fecha_creacion']
    search_fields = ['nombre', 'apellidos', 'correo']
    readonly_fields = ['fecha_creacion']

@admin.register(Encargado)
class EncargadoAdmin(admin.ModelAdmin):
    form = EncargadoForm
    list_display = ['nombre', 'apellidos', 'correo', 'fecha_creacion']
    search_fields = ['nombre', 'apellidos', 'correo']
    readonly_fields = ['fecha_creacion']

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    form = UsuarioForm
    list_display = ['nombre', 'apellidos', 'correo', 'carrera', 'activo', 'fecha_creacion']
    search_fields = ['nombre', 'apellidos', 'correo']
    list_filter = ['carrera', 'activo']
    readonly_fields = ['fecha_creacion']

@admin.register(Espacio)
class EspacioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'capacidad', 'ubicacion', 'carrera', 'encargado', 'activo', 'fecha_creacion']
    search_fields = ['nombre', 'ubicacion']
    list_filter = ['carrera', 'encargado', 'activo']
    readonly_fields = ['fecha_creacion']

@admin.register(Solicitud)
class SolicitudAdmin(admin.ModelAdmin):
    list_display = ['nombre_evento', 'espacio', 'usuario', 'estado', 'fecha_evento', 'fecha_creacion']
    search_fields = ['nombre_evento', 'usuario__nombre', 'usuario__apellidos']
    list_filter = ['estado', 'espacio', 'fecha_evento']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    date_hierarchy = 'fecha_evento'