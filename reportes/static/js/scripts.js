// ============================
// FUNCIONES COMUNES
// ============================
function toggleTheme() {
    const html = document.documentElement;
    const themeIcon = document.getElementById('theme-icon');
    const themeText = document.getElementById('theme-text');
    
    if (html.getAttribute('data-theme') === 'dark') {
        html.removeAttribute('data-theme');
        themeIcon.className = 'fas fa-moon';
        themeText.textContent = 'Modo Oscuro';
        localStorage.setItem('theme', 'light');
    } else {
        html.setAttribute('data-theme', 'dark');
        themeIcon.className = 'fas fa-sun';
        themeText.textContent = 'Modo Claro';
        localStorage.setItem('theme', 'dark');
    }
}

// Cargar tema guardado al iniciar
document.addEventListener('DOMContentLoaded', function() {
    const savedTheme = localStorage.getItem('theme');
    const themeIcon = document.getElementById('theme-icon');
    const themeText = document.getElementById('theme-text');
    
    if (savedTheme === 'dark' && themeIcon && themeText) {
        document.documentElement.setAttribute('data-theme', 'dark');
        themeIcon.className = 'fas fa-sun';
        themeText.textContent = 'Modo Claro';
    }
});

// ============================
// SCRIPTS DEL DASHBOARD ENCARGADO
// ============================
function initDashboardEncargado() {
    if (!document.getElementById('calendario-body')) return;

    let mesActual = 6; // Julio (0-11)
    let anioActual = 2025;
    const hoy = new Date();
    const nombresMeses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
    let eventos = {
        '2025-7-15': [{ nombre: 'Reunión Académica', espacio: 'Aula 101', color: '#1e3a8a' }],
        '2025-7-22': [{ nombre: 'Examen Final', espacio: 'Aula 205', color: '#dc2626' }],
        '2025-7-27': [{ nombre: 'Evento Especial', espacio: 'Patio Central', color: '#4cc9f0' }],
        '2025-7-30': [{ nombre: 'Clase Magistral', espacio: 'Aula Magna', color: '#fbbf24' }]
    };

    function generarCalendario() {
        const primerDia = new Date(anioActual, mesActual, 1);
        const ultimoDia = new Date(anioActual, mesActual + 1, 0);
        const diasEnMes = ultimoDia.getDate();
        const diaSemanaInicio = primerDia.getDay();
        const calendarioBody = document.getElementById('calendario-body');
        calendarioBody.innerHTML = '';
        let fecha = 1;
        let semanas = Math.ceil((diasEnMes + diaSemanaInicio) / 7);
        for (let semana = 0; semana < semanas; semana++) {
            const fila = calendarioBody.insertRow();
            for (let dia = 0; dia < 7; dia++) {
                const celda = fila.insertCell();
                if (semana === 0 && dia < diaSemanaInicio) {
                    celda.classList.add('dia-vacio');
                } else if (fecha > diasEnMes) {
                    celda.classList.add('dia-vacio');
                } else {
                    const esDiaActual = (fecha === hoy.getDate() && mesActual === hoy.getMonth() && anioActual === hoy.getFullYear());
                    if (esDiaActual) celda.classList.add('dia-actual');
                    const numeroDia = document.createElement('div');
                    numeroDia.className = 'numero-dia';
                    numeroDia.textContent = fecha;
                    const fechaKey = `${anioActual}-${mesActual + 1}-${fecha}`;
                    const eventosDelDia = eventos[fechaKey] || [];
                    if (eventosDelDia.length) {
                        numeroDia.classList.add('evento-presente');
                        eventosDelDia.forEach(evento => {
                            const tooltip = document.createElement('div');
                            tooltip.className = 'tooltip';
                            const marker = document.createElement('div');
                            marker.className = 'evento-marker';
                            marker.style.setProperty('--color-evento', evento.color);
                            const tooltipText = document.createElement('span');
                            tooltipText.className = 'tooltip-text';
                            tooltipText.textContent = `${evento.nombre} | ${evento.espacio}`;
                            tooltip.appendChild(marker);
                            tooltip.appendChild(tooltipText);
                            celda.appendChild(tooltip);
                        });
                    }
                    celda.appendChild(numeroDia);
                    celda.dataset.fecha = fechaKey;
                    celda.addEventListener('click', () => mostrarModal('editar', celda.dataset.fecha));
                    fecha++;
                }
            }
        }
        document.getElementById('titulo-mes').textContent = `${nombresMeses[mesActual]} ${anioActual}`;
    }

    window.cambiarMes = function(direccion) {
        mesActual += direccion;
        if (mesActual > 11) { mesActual = 0; anioActual++; }
        else if (mesActual < 0) { mesActual = 11; anioActual--; }
        generarCalendario();
    };

    window.mostrarModal = function(accion, fecha = null) {
        const modal = document.getElementById('modal');
        const modalTitle = document.getElementById('modal-title');
        const nombreInput = document.getElementById('nombre');
        const espacioInput = document.getElementById('espacio');
        const colorInput = document.getElementById('color');
        modal.style.display = 'block';
        if (accion === 'agregar') {
            modalTitle.textContent = 'Agregar Evento';
            nombreInput.value = '';
            espacioInput.value = '';
            colorInput.value = '#1e3a8a';
        } else if (accion === 'editar' && fecha) {
            modalTitle.textContent = 'Editar Evento';
            const eventosDelDia = eventos[fecha] || [];
            if (eventosDelDia.length) {
                const evento = eventosDelDia[0];
                nombreInput.value = evento.nombre;
                espacioInput.value = evento.espacio;
                colorInput.value = evento.color;
            }
        }
        document.getElementById('evento-form').onsubmit = (e) => {
            e.preventDefault();
            const nombre = nombreInput.value;
            const espacio = espacioInput.value;
            const color = colorInput.value;
            if (accion === 'agregar' && fecha === null) {
                const hoy = new Date();
                const fechaKey = `${hoy.getFullYear()}-${hoy.getMonth() + 1}-${hoy.getDate()}`;
                if (!eventos[fechaKey]) eventos[fechaKey] = [];
                eventos[fechaKey].push({ nombre, espacio, color });
            } else if (accion === 'editar' && fecha) {
                const eventosDelDia = eventos[fecha] || [];
                if (eventosDelDia.length) eventosDelDia[0] = { nombre, espacio, color };
            }
            cerrarModal();
            generarCalendario();
        };
    };

    window.cerrarModal = function() {
        document.getElementById('modal').style.display = 'none';
    };

    generarCalendario();
}

// ============================
// SCRIPTS DE LISTAR SOLICITUDES
// ============================
function initListarSolicitudes() {
    if (!document.getElementById('rejectModal')) return;

    let currentSolicitudId = null;

    window.openRejectModal = function(solicitudId, solicitanteName) {
        currentSolicitudId = solicitudId;
        document.getElementById('solicitanteName').textContent = solicitanteName;
        document.getElementById('rejectionReason').value = '';
        const modal = document.getElementById('rejectModal');
        modal.style.display = 'flex';
        setTimeout(() => {
            modal.querySelector('.modal').classList.add('show');
        }, 10);
    };

    window.closeRejectModal = function() {
        const modal = document.getElementById('rejectModal');
        modal.querySelector('.modal').classList.remove('show');
        setTimeout(() => {
            modal.style.display = 'none';
            currentSolicitudId = null;
        }, 300);
    };

    window.confirmReject = function() {
        const reason = document.getElementById('rejectionReason').value;
        const errorMessage = document.getElementById('errorMessage');
        if (!reason.trim()) {
            document.getElementById('rejectionReason').classList.add('error');
            errorMessage.style.display = 'flex';
            return;
        }
        document.getElementById('rejectionReason').classList.remove('error');
        errorMessage.style.display = 'none';

        // Aquí puedes agregar la lógica para enviar la información al servidor
        alert(`Solicitud ${currentSolicitudId} rechazada.${reason ? '\nRazón: ' + reason : ''}`);
        closeRejectModal();
    };

    document.getElementById('rejectModal').addEventListener('click', function(e) {
        if (e.target === this) {
            closeRejectModal();
        }
    });

    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeRejectModal();
        }
    });
}

// ============================
// SCRIPTS DE SOLICITUDES ACEPTADAS
// ============================
function initSolicitudesAceptadas() {
    if (!document.querySelector('.solicitudes-aceptadas')) return;
    // No se requiere lógica adicional para esta página, solo toggleTheme
}

// ============================
// SCRIPTS DE SOLICITUDES PENDIENTES
// ============================
function initSolicitudesPendientes() {
    if (!document.querySelector('.solicitudes-pendientes')) return;
    // No se requiere lógica adicional para esta página, solo toggleTheme
}

// ============================
// SCRIPTS DE GENERACIÓN DE REPORTES
// ============================
function initGenerarReportes() {
    if (!document.querySelector('.generar-reportes')) return;
    // No se requiere lógica adicional para esta página, solo toggleTheme
}

// ============================
// INICIALIZACIÓN
// ============================
document.addEventListener('DOMContentLoaded', function() {
    initDashboardEncargado();
    initListarSolicitudes();
    initSolicitudesAceptadas();
    initSolicitudesPendientes();
    initGenerarReportes();
});