from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Facultad, Carrera, Espacio, CustomUser, EspacioCampus
from gestion_espacios_academicos.forms import FacultadForm, CarreraForm, EspacioForm, EncargadoRegistrationForm, EspacioCampusForm

# Decorador para restringir acceso por tipo de usuario
def user_type_required(user_type):
    def decorator(view_func):
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if request.user.tipo_usuario != user_type:
                messages.error(request, 'Acceso denegado. No tienes permisos para esta acción.')
                return redirect('login')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

@user_type_required('administrador')
def dashboard_administrador(request):
    return render(request, 'administrador/dashboard_administrador.html')

@user_type_required('administrador')
def registrar_facultad(request):
    if request.method == 'POST':
        form = FacultadForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Facultad registrada con éxito.')
            return redirect('lista_facultades')
        else:
            messages.error(request, 'Error al registrar la facultad. Por favor, verifica los datos.')
    else:
        form = FacultadForm()
    return render(request, 'administrador/registrar_facultad.html', {'form': form})

@user_type_required('administrador')
def lista_facultades(request):
    facultades = Facultad.objects.all()
    return render(request, 'administrador/lista_facultades.html', {'facultades': facultades})

@user_type_required('administrador')
def editar_facultad(request, pk):
    facultad = get_object_or_404(Facultad, pk=pk)
    if request.method == 'POST':
        if 'delete' in request.POST:
            try:
                facultad.delete()
                messages.success(request, 'Facultad eliminada con éxito.')
                return redirect('lista_facultades')
            except Exception as e:
                messages.error(request, f'Error al eliminar la facultad: {str(e)}')
        else:
            form = FacultadForm(request.POST, instance=facultad)
            if form.is_valid():
                form.save()
                messages.success(request, 'Facultad actualizada con éxito.')
                return redirect('lista_facultades')
            else:
                messages.error(request, 'Error al actualizar la facultad. Por favor, verifica los datos.')
    else:
        form = FacultadForm(instance=facultad)
    return render(request, 'administrador/editar_facultad.html', {'form': form, 'facultad': facultad})

@user_type_required('administrador')
def registrar_carrera(request):
    if request.method == 'POST':
        form = CarreraForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Carrera registrada con éxito.')
            return redirect('lista_carreras')
        else:
            messages.error(request, 'Error al registrar la carrera. Por favor, verifica los datos.')
    else:
        form = CarreraForm()
    return render(request, 'administrador/registrar_carrera.html', {'form': form})

@user_type_required('administrador')
def lista_carreras(request):
    carreras = Carrera.objects.all()
    return render(request, 'administrador/lista_carreras.html', {'carreras': carreras})

@user_type_required('administrador')
def editar_carrera(request, pk):
    carrera = get_object_or_404(Carrera, pk=pk)
    if request.method == 'POST':
        if 'delete' in request.POST:
            try:
                carrera.delete()
                messages.success(request, 'Carrera eliminada con éxito.')
                return redirect('lista_carreras')
            except Exception as e:
                messages.error(request, f'Error al eliminar la carrera: {str(e)}')
        else:
            form = CarreraForm(request.POST, instance=carrera)
            if form.is_valid():
                form.save()
                messages.success(request, 'Carrera actualizada con éxito.')
                return redirect('lista_carreras')
            else:
                messages.error(request, 'Error al actualizar la carrera. Por favor, verifica los datos.')
    else:
        form = CarreraForm(instance=carrera)
    return render(request, 'administrador/editar_carrera.html', {'form': form, 'carrera': carrera})

@user_type_required('administrador')
def registrar_espacios(request):
    if request.method == 'POST':
        form = EspacioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Espacio registrado con éxito.')
            return redirect('lista_espacios')
        else:
            messages.error(request, 'Error al registrar el espacio. Por favor, verifica los datos.')
    else:
        form = EspacioForm()
    return render(request, 'administrador/registrar_espacios.html', {'form': form})

@user_type_required('administrador')
def lista_espacios(request):
    try:
        # Espacios de carrera y facultad
        espacios_carrera = Espacio.objects.select_related('carrera__facultad').filter(carrera__isnull=False)
        espacios_facultad = Espacio.objects.filter(carrera__isnull=True, facultad__isnull=False)
        espacios_campus = EspacioCampus.objects.all()

        # Combinar todos los espacios en una lista de diccionarios
        all_espacios = []
        for espacio in espacios_carrera:
            all_espacios.append({
                'tipo': 'Carrera',
                'nombre': espacio.nombre,
                'facultad': espacio.carrera.facultad.nombre if espacio.carrera.facultad else 'Común',
                'carrera': espacio.carrera.nombre if espacio.carrera else 'Sin carrera',
                'ubicacion': None,
                'capacidad': None,
                'descripcion': espacio.descripción,
                'id': espacio.id,
                'es_campus': False
            })
        for espacio in espacios_facultad:
            all_espacios.append({
                'tipo': 'Facultad',
                'nombre': espacio.nombre,
                'facultad': espacio.facultad.nombre if espacio.facultad else 'Sin facultad',
                'carrera': None,
                'ubicacion': None,
                'capacidad': None,
                'descripcion': espacio.descripción,
                'id': espacio.id,
                'es_campus': False
            })
        for espacio in espacios_campus:
            all_espacios.append({
                'tipo': 'Campus',
                'nombre': espacio.nombre,
                'facultad': None,
                'carrera': None,
                'ubicacion': espacio.ubicacion,
                'capacidad': espacio.capacidad,
                'descripcion': espacio.descripcion,
                'id': espacio.id,
                'es_campus': True
            })

        context = {
            'all_espacios': all_espacios
        }
        if messages.get_messages(request):
            context['messages'] = messages.get_messages(request)
        return render(request, 'administrador/lista_espacios.html', context)
    except Exception as e:
        messages.error(request, f"Error al cargar la lista de espacios: {str(e)}")
        return render(request, 'administrador/lista_espacios.html', {'all_espacios': []})

@user_type_required('administrador')
def editar_espacios(request, pk):
    espacio = get_object_or_404(Espacio, pk=pk)
    if request.method == 'POST':
        if 'delete' in request.POST:
            try:
                espacio.delete()
                messages.success(request, 'Espacio eliminado con éxito.')
                return redirect('lista_espacios')
            except Exception as e:
                messages.error(request, f'Error al eliminar el espacio: {str(e)}')
        else:
            form = EspacioForm(request.POST, instance=espacio)
            if form.is_valid():
                form.save()
                messages.success(request, 'Espacio actualizado con éxito.')
                return redirect('lista_espacios')
            else:
                messages.error(request, 'Error al actualizar el espacio. Por favor, verifica los datos.')
    else:
        form = EspacioForm(instance=espacio)
    return render(request, 'administrador/editar_espacios.html', {'form': form, 'espacio': espacio})

@user_type_required('administrador')
def registrar_encargados(request):
    if request.method == 'POST':
        form = EncargadoRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.tipo_usuario = 'encargado'
            user.save()
            messages.success(request, 'Encargado registrado con éxito.')
            return redirect('lista_encargados')
        else:
            messages.error(request, 'Error al registrar el encargado. Por favor, verifica los datos.')
    else:
        form = EncargadoRegistrationForm()
    return render(request, 'administrador/registrar_encargados.html', {'form': form})

@user_type_required('administrador')
def lista_encargados(request):
    encargados = CustomUser.objects.filter(tipo_usuario='encargado')
    return render(request, 'administrador/lista_encargados.html', {'encargados': encargados})

@user_type_required('administrador')
def editar_encargado(request, pk):
    encargado = get_object_or_404(CustomUser, pk=pk, tipo_usuario='encargado')
    if request.method == 'POST':
        if 'delete' in request.POST:
            try:
                encargado.delete()
                messages.success(request, 'Encargado eliminado con éxito.')
                return redirect('lista_encargados')
            except Exception as e:
                messages.error(request, f'Error al eliminar el encargado: {str(e)}')
        else:
            form = EncargadoRegistrationForm(request.POST, instance=encargado)
            if form.is_valid():
                form.save()
                messages.success(request, 'Encargado actualizado con éxito.')
                return redirect('lista_encargados')
            else:
                messages.error(request, 'Error al actualizar el encargado. Por favor, verifica los datos.')
    else:
        form = EncargadoRegistrationForm(instance=encargado)
    return render(request, 'administrador/editar_encargado.html', {'form': form, 'encargado': encargado})