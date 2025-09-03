/* ============================
   CALENDARIO USUARIO – EVENTOS DE CARRERA, FACULTAD Y CAMPUS
   ============================ */

async function cargarEventosUsuario() {
    try {
        const res = await fetch('/usuarios/api/eventos-usuario/');
        const data = await res.json();
        const eventosMap = {};

        data.forEach(e => {
            const key = e.fecha;
            if (!eventosMap[key]) eventosMap[key] = [];
            eventosMap[key].push({
                nombre: e.nombre_evento,
                espacio: e.espacio__nombre,
                color: '#4cc9f0' // azul suave
            });
        });
        return eventosMap;
    } catch (err) {
        console.error('Error al cargar eventos del usuario:', err);
        return {};
    }
}

async function generarCalendario() {
    const hoy = new Date();
    let mesActual = hoy.getMonth();
    let anioActual = hoy.getFullYear();
    const nombresMeses = [
        'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ];

    const eventos = await cargarEventosUsuario();

    const primerDia = new Date(anioActual, mesActual, 1).getDay();
    const diasMes = new Date(anioActual, mesActual + 1, 0).getDate();
    const tbody = document.getElementById('calendario-body');
    if (!tbody) return;

    tbody.innerHTML = '';
    let fecha = 1;

    for (let sem = 0; sem < 6; sem++) {
        const row = document.createElement('tr');
        for (let dia = 0; dia < 7; dia++) {
            const cell = document.createElement('td');
            if (sem === 0 && dia < primerDia) {
                cell.classList.add('dia-vacio');
            } else if (fecha > diasMes) {
                cell.classList.add('dia-vacio');
            } else {
                const hoyCheck = fecha === hoy.getDate() && mesActual === hoy.getMonth() && anioActual === hoy.getFullYear();
                if (hoyCheck) cell.classList.add('dia-actual');

                const numero = document.createElement('div');
                numero.className = 'numero-dia';
                numero.textContent = fecha;

                const fechaKey = `${anioActual}-${mesActual + 1}-${fecha}`;
                const eventosDelDia = eventos[fechaKey] || [];

                eventosDelDia.forEach(ev => {
                    numero.classList.add('evento-presente');
                    const tooltip = document.createElement('div');
                    tooltip.className = 'tooltip';

                    const marker = document.createElement('div');
                    marker.className = 'evento-marker';
                    marker.style.backgroundColor = ev.color;

                    const tooltipText = document.createElement('span');
                    tooltipText.className = 'tooltip-text';
                    tooltipText.textContent = `${ev.nombre} | ${ev.espacio}`;

                    tooltip.appendChild(marker);
                    tooltip.appendChild(tooltipText);
                    cell.appendChild(tooltip);
                });

                cell.appendChild(numero);
                fecha++;
            }
            row.appendChild(cell);
        }
        tbody.appendChild(row);
    }

    const titulo = document.getElementById('titulo-mes');
    if (titulo) {
        titulo.textContent = `${nombresMeses[mesActual]} ${anioActual}`;
    }
}

// Navegación
let mesActualU = new Date().getMonth();
let anioActualU = new Date().getFullYear();

window.cambiarMesUsuario = function (delta) {
    mesActualU += delta;
    if (mesActualU < 0) { mesActualU = 11; anioActualU--; }
    if (mesActualU > 11) { mesActualU = 0; anioActualU++; }
    generarCalendario();
};

// Inicializar
document.addEventListener('DOMContentLoaded', () => {
    generarCalendario();
});