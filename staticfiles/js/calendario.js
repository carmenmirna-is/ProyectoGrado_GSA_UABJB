/* ============================
   CALENDARIO USUARIO – EVENTOS DE CARRERA, FACULTAD Y CAMPUS
   Muestra TODAS las reservas aceptadas (propias en azul, otras en gris)
   ============================ */

// Variables globales para la navegación
let mesActualU = new Date().getMonth();
let anioActualU = new Date().getFullYear();

async function cargarEventosUsuario() {
    try {
        console.log('🔄 Cargando eventos del usuario...');
        const res = await fetch('/usuarios/api/eventos-usuario/');
        
        if (!res.ok) {
            throw new Error(`Error HTTP: ${res.status}`);
        }
        
        const data = await res.json();
        console.log('📅 Datos recibidos del servidor:', data);
        console.log(`📊 Total de eventos: ${data.length}`);
        
        const eventosMap = {};

        data.forEach(e => {
            const key = e.fecha;
            console.log(`📌 Procesando evento: ${e.nombre_evento} - Fecha: ${key} - Es mío: ${e.es_mio}`);
            
            if (!eventosMap[key]) eventosMap[key] = [];
            
            // 🎨 Color diferente según sea del usuario o de otros
            const color = e.es_mio ? '#3b82f6' : '#94a3b8'; // Azul para propios, gris para otros
            const icono = e.es_mio ? '✅' : '📅';
            
            console.log(`🎨 Asignando color: ${color} para evento ${e.nombre_evento} (es_mio: ${e.es_mio})`);
            
            eventosMap[key].push({
                nombre: e.nombre_evento,
                espacio: e.espacio__nombre,
                solicitante: e.solicitante,
                esMio: e.es_mio,
                color: color,
                icono: icono,
                descripcion: e.descripcion || '',
                tipoEspacio: e.tipo_espacio
            });
        });
        
        console.log('🗺️ Mapa de eventos generado:', eventosMap);
        console.log(`📍 Días con eventos: ${Object.keys(eventosMap).length}`);
        return eventosMap;
        
    } catch (err) {
        console.error('❌ Error al cargar eventos del usuario:', err);
        return {};
    }
}

async function generarCalendario() {
    console.log(`📅 Generando calendario para ${mesActualU + 1}/${anioActualU}`);
    
    const nombresMeses = [
        'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ];

    const eventos = await cargarEventosUsuario();
    console.log('🎯 Eventos cargados para el calendario:', eventos);

    const primerDia = new Date(anioActualU, mesActualU, 1).getDay();
    const diasMes = new Date(anioActualU, mesActualU + 1, 0).getDate();
    const tbody = document.getElementById('calendario-body');
    
    if (!tbody) {
        console.error('❌ No se encontró el elemento calendario-body');
        return;
    }

    tbody.innerHTML = '';
    let fecha = 1;

    // Para verificar el día actual
    const hoy = new Date();

    for (let sem = 0; sem < 6; sem++) {
        const row = document.createElement('tr');
        for (let dia = 0; dia < 7; dia++) {
            const cell = document.createElement('td');
            if (sem === 0 && dia < primerDia) {
                cell.classList.add('dia-vacio');
            } else if (fecha > diasMes) {
                cell.classList.add('dia-vacio');
            } else {
                // Verificar si es el día actual
                const hoyCheck = fecha === hoy.getDate() && 
                                mesActualU === hoy.getMonth() && 
                                anioActualU === hoy.getFullYear();
                if (hoyCheck) cell.classList.add('dia-actual');

                const numero = document.createElement('div');
                numero.className = 'numero-dia';
                numero.textContent = fecha;

                // Formato de fecha YYYY-MM-DD
                const fechaKey = `${anioActualU}-${String(mesActualU + 1).padStart(2, '0')}-${String(fecha).padStart(2, '0')}`;
                
                let eventosDelDia = eventos[fechaKey] || [];
                
                if (eventosDelDia.length > 0) {
                    console.log(`✅ ${eventosDelDia.length} eventos para ${fechaKey}:`, eventosDelDia);
                    numero.classList.add('evento-presente');
                    
                    // 🔥 AGREGAR CONTADOR DE EVENTOS
                    if (eventosDelDia.length > 1) {
                        const contador = document.createElement('span');
                        contador.className = 'contador-eventos';
                        contador.textContent = eventosDelDia.length;
                        numero.appendChild(contador);
                    }
                }

                // 📋 CREAR MARKERS Y TOOLTIPS PARA CADA EVENTO
                const markersContainer = document.createElement('div');
                markersContainer.className = 'markers-container';
                
                eventosDelDia.forEach((ev, index) => {
                    console.log(`🎨 Agregando evento visual: ${ev.nombre} con color ${ev.color}`);
                    
                    // 🔴 CREAR MARKER VISUAL (círculo de color)
                    const marker = document.createElement('div');
                    marker.className = 'evento-marker';
                    marker.style.backgroundColor = ev.color; // ✅ Aplicar color correcto
                    marker.title = `${ev.nombre} - ${ev.solicitante}`; // Tooltip nativo simple
                    
                    // 📝 CREAR TOOLTIP COMPLETO
                    const tooltip = document.createElement('div');
                    tooltip.className = 'tooltip';

                    const tooltipText = document.createElement('span');
                    tooltipText.className = 'tooltip-text';
                    
                    // 🎯 TOOLTIP MEJORADO CON MÁS INFO
                    const etiquetaMia = ev.esMio ? '✨ TU RESERVA' : `👤 ${ev.solicitante}`;
                    tooltipText.innerHTML = `
                        <strong>${ev.icono} ${ev.nombre}</strong>
                        <small style="color: ${ev.color};">${etiquetaMia}</small>
                        📍 ${ev.espacio}<br>
                        🏢 ${ev.tipoEspacio}
                        ${ev.descripcion ? `<br>📝 ${ev.descripcion}` : ''}
                    `;

                    tooltip.appendChild(tooltipText);
                    
                    // ✅ AGREGAR MARKER CON SU TOOLTIP
                    marker.appendChild(tooltip);
                    markersContainer.appendChild(marker);
                });
                
                // Agregar todos los markers al cell
                cell.appendChild(markersContainer);

                cell.appendChild(numero);
                fecha++;
            }
            row.appendChild(cell);
        }
        tbody.appendChild(row);
    }

    // Actualizar el título del mes
    const titulo = document.getElementById('titulo-mes');
    if (titulo) {
        titulo.textContent = `${nombresMeses[mesActualU]} ${anioActualU}`;
    }
    
    // 📊 MOSTRAR ESTADÍSTICAS
    mostrarEstadisticas(eventos);
    
    console.log('✅ Calendario generado completamente');
}

// 📊 Función para mostrar estadísticas de eventos
function mostrarEstadisticas(eventos) {
    let totalEventos = 0;
    let misPropios = 0;
    let deOtros = 0;
    
    Object.values(eventos).forEach(eventosDelDia => {
        eventosDelDia.forEach(ev => {
            totalEventos++;
            if (ev.esMio) misPropios++;
            else deOtros++;
        });
    });
    
    console.log(`📊 Estadísticas del mes:
    - Total de eventos: ${totalEventos}
    - Mis reservas: ${misPropios}
    - Reservas de otros: ${deOtros}`);
    
    // Actualizar el DOM si existe un elemento de estadísticas
    const statsEl = document.getElementById('calendario-stats');
    if (statsEl) {
        statsEl.innerHTML = `
            <div class="stats-container" style="display: flex; gap: 20px; justify-content: center; padding: 15px; background: #f8fafc; border-radius: 8px; margin-top: 10px;">
                <span class="stat-item" style="display: flex; align-items: center; gap: 5px;">
                    <span class="stat-icon" style="color: #3b82f6; font-size: 20px;">●</span>
                    Mis reservas: <strong>${misPropios}</strong>
                </span>
                <span class="stat-item" style="display: flex; align-items: center; gap: 5px;">
                    <span class="stat-icon" style="color: #94a3b8; font-size: 20px;">●</span>
                    Otras reservas: <strong>${deOtros}</strong>
                </span>
                <span class="stat-item" style="display: flex; align-items: center; gap: 5px;">
                    📅 Total: <strong>${totalEventos}</strong>
                </span>
            </div>
        `;
    }
}

// Función de navegación entre meses
window.cambiarMes = function (delta) {
    console.log('🔄 Navegando con delta:', delta);
    mesActualU += delta;
    if (mesActualU < 0) { 
        mesActualU = 11; 
        anioActualU--; 
    }
    if (mesActualU > 11) { 
        mesActualU = 0; 
        anioActualU++; 
    }
    console.log(`📅 Nuevo mes: ${mesActualU + 1}/${anioActualU}`);
    generarCalendario();
};

// Inicializar al cargar la página
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Inicializando calendario del usuario...');
    generarCalendario();
});