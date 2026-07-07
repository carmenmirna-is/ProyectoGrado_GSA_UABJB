from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from gestion_espacios_academicos.models import Facultad, Carrera, Espacio, CustomUser, EspacioCampus
from gestion_espacios_academicos.forms import (
    FacultadForm, CarreraForm, EspacioForm,
    EncargadoRegistrationForm, EspacioCampusForm
)
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required

@login_required
@never_cache  # 🔥 CRÍTICO: No cachear
def dashboard_administrador(request):
    """
    Dashboard del administrador del sistema
    """
    user = request.user
    
    # 🔒 Verificar que sea administrador
    if user.tipo_usuario != 'administrador':
        messages.error(request, '⛔ No tienes permiso para acceder a esta página.')
        return redirect('login')
    
    # 🔍 Debug: Verificar sesión
    print(f"👨‍💼 Dashboard Admin: {user.username} (ID: {user.id}, Rol: {user.tipo_usuario})")
    print(f"   Session Key: {request.session.session_key}")
    
    context = {
        'usuario': user,  # ✅ Pasar usuario explícitamente
        'administrador': user,  # ✅ Alias para templates
        'session_key': request.session.session_key[:10],  # Para debugging
    }
    
    return render(request, 'administrador/dashboard_administrador.html', context)

# ================= Facultades =================
def registrar_facultad(request):
    if request.method == 'POST':
        form = FacultadForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Facultad registrada con éxito.')
            return redirect('administrador:lista_facultades')  # ✅ CORREGIDO
        else:
            messages.error(request, 'Error al registrar la facultad. Verifica los datos.')
    else:
        form = FacultadForm()
    return render(request, 'administrador/registrar_facultad.html', {'form': form})

def lista_facultades(request):
    facultades = Facultad.objects.all()
    return render(request, 'administrador/lista_facultades.html', {'facultades': facultades})

def editar_facultad(request, pk):
    facultad = get_object_or_404(Facultad, pk=pk)
    if request.method == 'POST':
        if 'delete' in request.POST:
            try:
                facultad.delete()
                messages.success(request, 'Facultad eliminada con éxito.')
                return redirect('administrador:lista_facultades')  # ✅ CORREGIDO
            except Exception as e:
                messages.error(request, f'Error al eliminar la facultad: {str(e)}')
        else:
            form = FacultadForm(request.POST, instance=facultad)
            if form.is_valid():
                form.save()
                messages.success(request, 'Facultad actualizada con éxito.')
                return redirect('administrador:lista_facultades')  # ✅ CORREGIDO
            else:
                messages.error(request, 'Error al actualizar la facultad. Verifica los datos.')
    else:
        form = FacultadForm(instance=facultad)
    return render(request, 'administrador/editar_facultad.html', {'form': form, 'facultad': facultad})

# ================= Carreras =================
def registrar_carrera(request):
    if request.method == 'POST':
        form = CarreraForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Carrera registrada con éxito.')
            return redirect('administrador:lista_carreras')  # ✅ CORREGIDO
        else:
            messages.error(request, 'Error al registrar la carrera. Verifica los datos.')
    else:
        form = CarreraForm()
    return render(request, 'administrador/registrar_carrera.html', {'form': form})

def lista_carreras(request):
    carreras = Carrera.objects.all()
    return render(request, 'administrador/lista_carreras.html', {'carreras': carreras})

def editar_carrera(request, pk):
    carrera = get_object_or_404(Carrera, pk=pk)
    if request.method == 'POST':
        if 'delete' in request.POST:
            try:
                carrera.delete()
                messages.success(request, 'Carrera eliminada con éxito.')
                return redirect('administrador:lista_carreras')  # ✅ CORREGIDO
            except Exception as e:
                messages.error(request, f'Error al eliminar la carrera: {str(e)}')
        else:
            form = CarreraForm(request.POST, instance=carrera)
            if form.is_valid():
                form.save()
                messages.success(request, 'Carrera actualizada con éxito.')
                return redirect('administrador:lista_carreras')  # ✅ CORREGIDO
            else:
                messages.error(request, 'Error al actualizar la carrera. Verifica los datos.')
    else:
        form = CarreraForm(instance=carrera)
    return render(request, 'administrador/editar_carrera.html', {'form': form, 'carrera': carrera})

# ================= Espacios =================
def registrar_espacios(request):
    if request.method == 'POST':
        form = EspacioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Espacio registrado con éxito.')
            return redirect('administrador:lista_espacios')  # ✅ Ya está correcto
        else:
            messages.error(request, 'Error al registrar el espacio. Verifica los datos.')
    else:
        form = EspacioForm()
    return render(request, 'administrador/registrar_espacios.html', {'form': form})

def registrar_espacio_campus(request):
    if request.method == 'POST':
        # ⚠️ IMPORTANTE: Agregar request.FILES para que acepte archivos
        form = EspacioCampusForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Espacio registrado exitosamente')
            return redirect('administrador:lista_espacios')
    else:
        form = EspacioCampusForm()
    return render(request, 'administrador/registrar_espacio_campus.html', {'form': form})

def lista_espacios(request):
    try:
        espacios_carrera = Espacio.objects.select_related('carrera__facultad').filter(activo=True)

        all_espacios = []
        for espacio in espacios_carrera:
            all_espacios.append({
                'tipo': 'Carrera',
                'nombre': espacio.nombre,
                'facultad': espacio.carrera.facultad.nombre if espacio.carrera and espacio.carrera.facultad else 'Sin facultad',
                'carrera': espacio.carrera.nombre if espacio.carrera else 'Sin carrera',
                'ubicacion': espacio.ubicacion,
                'capacidad': espacio.capacidad,
                'descripcion': espacio.descripcion,
                'id': espacio.id,
                'es_campus': False
            })

        return render(request, 'administrador/lista_espacios.html', {'all_espacios': all_espacios})

    except Exception as e:
        messages.error(request, f"Error al cargar la lista de espacios: {str(e)}")
        return render(request, 'administrador/lista_espacios.html', {'all_espacios': []})
    
def lista_espacios_campus(request):
    espacios_campus = EspacioCampus.objects.all()
    all_espacios = []
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
                'es_campus': True,
                'encargado': espacio.encargado,
            })
    return render(request, 'administrador/lista_espacios_campus.html', {'espacios': all_espacios})

def editar_espacios(request, pk):
    espacio = get_object_or_404(Espacio, pk=pk)
    if request.method == 'POST':
        if 'delete' in request.POST:
            try:
                espacio.delete()
                messages.success(request, 'Espacio eliminado con éxito.')
                return redirect('administrador:lista_espacios')  # ✅ Ya está correcto
            except Exception as e:
                messages.error(request, f'Error al eliminar el espacio: {str(e)}')
        else:
            form = EspacioForm(request.POST, instance=espacio)
            if form.is_valid():
                form.save()
                messages.success(request, 'Espacio actualizado con éxito.')
                return redirect('administrador:lista_espacios')  # ✅ Ya está correcto
            else:
                messages.error(request, 'Error al actualizar el espacio. Verifica los datos.')
    else:
        form = EspacioForm(instance=espacio)
    return render(request, 'administrador/editar_espacios.html', {'form': form, 'espacio': espacio})

def editar_espacio_campus(request, pk):
    espacio = get_object_or_404(EspacioCampus, pk=pk)

    if request.method == 'POST':
        if 'delete' in request.POST:
            espacio.delete()
            messages.success(request, 'Espacio de campus eliminado con éxito.')
            return redirect('administrador:lista_espacios_campus')

        form = EspacioCampusForm(request.POST, instance=espacio)
        if form.is_valid():
            form.save()
            messages.success(request, 'Espacio de campus actualizado con éxito.')
            return redirect('administrador:lista_espacios_campus')
        else:
            messages.error(request, 'Error al actualizar el espacio de campus. Revisa los datos.')

    else:
        form = EspacioCampusForm(instance=espacio)

    return render(request, 'administrador/editar_espacio_campus.html', {'form': form, 'espacio': espacio})

# ================= Encargados =================
def registrar_encargados(request):
    if request.method == 'POST':
        form = EncargadoRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.tipo_usuario = 'encargado'
            user.save()
            messages.success(request, 'Encargado registrado con éxito.')
            return redirect('administrador:lista_encargados')  # ✅ Ya está correcto
        else:
            messages.error(request, 'Error al registrar el encargado. Verifica los datos.')
    else:
        form = EncargadoRegistrationForm()
    return render(request, 'administrador/registrar_encargados.html', {'form': form})

def lista_encargados(request):
    encargados = CustomUser.objects.filter(tipo_usuario='encargado')
    return render(request, 'administrador/lista_encargados.html', {'encargados': encargados})

def editar_encargado(request, pk):
    encargado = get_object_or_404(CustomUser, pk=pk, tipo_usuario='encargado')
    if request.method == 'POST':
        if 'delete' in request.POST:
            try:
                encargado.delete()
                messages.success(request, 'Encargado eliminado con éxito.')
                return redirect('administrador:lista_encargados')  # ✅ CORREGIDO
            except Exception as e:
                messages.error(request, f'Error al eliminar el encargado: {str(e)}')
        else:
            form = EncargadoRegistrationForm(request.POST, instance=encargado)
            if form.is_valid():
                form.save()
                messages.success(request, 'Encargado actualizado con éxito.')
                return redirect('administrador:lista_encargados')  # ✅ CORREGIDO
            else:
                messages.error(request, 'Error al actualizar el encargado. Verifica los datos.')
    else:
        form = EncargadoRegistrationForm(instance=encargado)
    return render(request, 'administrador/editar_encargado.html', {'form': form, 'encargado': encargado})  # ✅ CORREGIDO: faltaba .html