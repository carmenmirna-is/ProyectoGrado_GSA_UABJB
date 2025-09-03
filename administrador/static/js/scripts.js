function toggleTheme() {
    const body = document.body;
    const themeIcon = document.getElementById('theme-icon');
    const themeText = document.getElementById('theme-text');
    if (body.getAttribute('data-theme') === 'dark') {
        body.removeAttribute('data-theme');
        themeIcon.className = 'fas fa-moon';
        themeText.textContent = 'Modo Oscuro';
    } else {
        body.setAttribute('data-theme', 'dark');
        themeIcon.className = 'fas fa-sun';
        themeText.textContent = 'Modo Claro';
    }
}

// Función para actualizar las carreras según la facultad seleccionada
function updateCarreras() {
    const facultadSelect = document.getElementById('facultad');
    const carreraSelect = document.getElementById('carrera');
    if (!facultadSelect || !carreraSelect) return; // Salir si los elementos no existen

    const facultadId = facultadSelect.value;

    // Simulación de datos (deberías reemplazar esto con una llamada AJAX real si usas Django)
    const carrerasPorFacultad = {
        1: ['Ingeniería Civil', 'Ingeniería Eléctrica'],
        2: ['Medicina', 'Enfermería'],
        3: ['Derecho', 'Ciencias Políticas']
    };

    carreraSelect.innerHTML = '<option value="">Seleccione una carrera</option>';
    if (facultadId) {
        const carreras = carrerasPorFacultad[facultadId] || [];
        carreras.forEach(carrera => {
            const option = document.createElement('option');
            option.value = carrera.toLowerCase().replace(/ /g, '_');
            option.textContent = carrera;
            carreraSelect.appendChild(option);
        });

        // Seleccionar la carrera actual si existe (para editar)
        const currentCarrera = "{{ espacio.carrera_nombre|lower|replace(' ', '_') }}";
        if (currentCarrera && currentCarrera !== "{{ espacio.carrera_nombre|lower|replace(' ', '_') }}") {
            carreraSelect.value = currentCarrera;
        }
    }
}

// Ejecutar updateCarreras al cargar la página si los elementos existen
window.onload = function() {
    if (document.getElementById('facultad') && document.getElementById('carrera')) {
        updateCarreras();
    }
};