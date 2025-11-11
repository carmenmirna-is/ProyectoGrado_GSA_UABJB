/* ============================
   DASHBOARD ENCARGADO - CALENDARIO CON EVENTOS ACEPTADOS
   ============================ */

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
        themeIcon.className = 'fas faz-sun';
        themeText.textContent = 'Modo Claro';
        localStorage.setItem('theme', 'dark');
    }
}

/* ============================
   INICIALIZACIÓN DEL CALENDARIO
   ============================ */
async function initDashboardEncargado() {
    if (!document.getElementById('calendario-body')) return;

    const hoy = new Date();
    let mesActual = hoy.getMonth();
    let anioActual = hoy.getFullYear();
    const nombresMeses = [
        'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ];

    let eventos = {};

    async function cargarSolicitudesAceptadas() {
        try {
            const res = await fetch('/encargados/api/solicitudes-aceptadas/');
            const data = await res.json();
            const eventosMap = {};

            data.forEach(s => {
                const key = s.fecha;
                if (!eventosMap[key]) eventosMap[key] = [];
                eventosMap[key].push({
                    nombre: s.nombre_evento,
                    espacio: s.espacio__nombre || s.espacio,
                    tipo_espacio: s.tipo_espacio,
                    usuario: s.nombre_usuario,
                    hora: s.hora,
                    color: '#10b981'
                });
            });

            return eventosMap;
        } catch (err) {
            console.error('Error al cargar solicitudes aceptadas:', err);
            return {};
        }
    }

    async function generarCalendario() {
        eventos = await cargarSolicitudesAceptadas();

        const primerDia = new Date(anioActual, mesActual, 1);
        const ultimoDia = new Date(anioActual, mesActual + 1, 0);
        const diasEnMes = ultimoDia.getDate();
        const diaSemanaInicio = primerDia.getDay();
        const calendarioBody = document.getElementById('calendario-body');
        calendarioBody.innerHTML = '';

        let fecha = 1;
        const semanas = Math.ceil((diasEnMes + diaSemanaInicio) / 7);

        for (let semana = 0; semana < semanas; semana++) {
            const fila = calendarioBody.insertRow();
            for (let dia = 0; dia < 7; dia++) {
                const celda = fila.insertCell();

                if (semana === 0 && dia < diaSemanaInicio) {
                    celda.classList.add('dia-vacio');
                } else if (fecha > diasEnMes) {
                    celda.classList.add('dia-vacio');
                } else {
                    const esDiaActual = fecha === hoy.getDate() && mesActual === hoy.getMonth() && anioActual === hoy.getFullYear();
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
                            marker.style.backgroundColor = evento.color;

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
                    fecha++;
                }
            }
        }

        document.getElementById('titulo-mes').textContent = `${nombresMeses[mesActual]} ${anioActual}`;
    }

    window.cambiarMes = function (direccion) {
        mesActual += direccion;
        if (mesActual > 11) {
            mesActual = 0;
            anioActual++;
        } else if (mesActual < 0) {
            mesActual = 11;
            anioActual--;
        }
        generarCalendario();
    };

    await generarCalendario();
}

/* ============================
   FUNCIONES MODAL CREAR EVENTO
   ============================ */

window.mostrarModalCrearEvento = function () {
    const modal = document.getElementById('modalCrearEvento');
    if (modal) {
        modal.style.display = 'flex';
    } else {
        console.error('No se encontró el modal con ID "modalCrearEvento"');
    }
};

window.cerrarModalCrearEvento = function () {
    const modal = document.getElementById('modalCrearEvento');
    if (modal) {
        modal.style.display = 'none';
    }
};

// Cerrar modal con clic fuera o ESC
document.addEventListener('click', function (e) {
    const modal = document.getElementById('modalCrearEvento');
    if (modal && e.target === modal) {
        cerrarModalCrearEvento();
    }
});

document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
        cerrarModalCrearEvento();
    }
});

/* ============================
   ENVÍO DEL FORMULARIO CREAR EVENTO
   ============================ */
document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('formCrearEvento');
    if (!form) return;

    form.addEventListener('submit', async function (e) {
        e.preventDefault();

        const formData = new FormData(this);
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

        if (!csrfToken) {
            alert('No se encontró el token CSRF');
            return;
        }

        const submitBtn = this.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creando...';
        submitBtn.disabled = true;

        try {
            const res = await fetch('/encargados/crear-evento/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': csrfToken
                }
            });

            if (!res.ok) {
                const text = await res.text();
                console.error('Respuesta del servidor:', text);
                alert('Error del servidor:\n' + text);
                return;
            }

            const data = await res.json();

            if (data.status === 'success') {
                alert(data.message);
                cerrarModalCrearEvento();
                form.reset();
                await initDashboardEncargado(); // ✅ Recarga el calendario
            } else {
                alert(data.message || 'Error al crear el evento');
            }
        } catch (err) {
            console.error('Error al crear evento:', err);
            alert('Error de conexión');
        } finally {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    });
});

/* ============================
   INICIALIZAR TODO
   ============================ */
document.addEventListener('DOMContentLoaded', async () => {
    await initDashboardEncargado();
});