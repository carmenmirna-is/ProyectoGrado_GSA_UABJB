/* ============================
   CALENDARIO USUARIO – EVENTOS DE CARRERA, FACULTAD Y CAMPUS (CON DEBUG)
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
        
        const eventosMap = {};

        data.forEach(e => {
            const key = e.fecha;
            console.log(`📌 Procesando evento: ${e.nombre_evento} - Fecha: ${key}`);
            
            if (!eventosMap[key]) eventosMap[key] = [];
            eventosMap[key].push({
                nombre: e.nombre_evento,
                espacio: e.espacio__nombre,
                color: '#4cc9f0' // azul suave
            });
        });
        
        console.log('🗺️ Mapa de eventos generado:', eventosMap);
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

    // IMPORTANTE: Usar las variables globales de navegación
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
                // Verificar si es el día actual usando las variables globales
                const hoyCheck = fecha === hoy.getDate() && 
                                mesActualU === hoy.getMonth() && 
                                anioActualU === hoy.getFullYear();
                if (hoyCheck) cell.classList.add('dia-actual');

                const numero = document.createElement('div');
                numero.className = 'numero-dia';
                numero.textContent = fecha;

                // Probar diferentes formatos de fecha
                const fechaKey1 = `${anioActualU}-${String(mesActualU + 1).padStart(2, '0')}-${String(fecha).padStart(2, '0')}`;
                const fechaKey2 = `${anioActualU}-${mesActualU + 1}-${fecha}`;
                
                console.log(`🔍 Buscando eventos para fecha ${fecha}: formato1=${fechaKey1}, formato2=${fechaKey2}`);
                
                let eventosDelDia = eventos[fechaKey1] || eventos[fechaKey2] || [];
                
                if (eventosDelDia.length > 0) {
                    console.log(`✅ Encontrados ${eventosDelDia.length} eventos para el día ${fecha}:`, eventosDelDia);
                }

                eventosDelDia.forEach(ev => {
                    console.log(`🎨 Agregando evento visual: ${ev.nombre}`);
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

    // Actualizar el título usando las variables globales
    const titulo = document.getElementById('titulo-mes');
    if (titulo) {
        titulo.textContent = `${nombresMeses[mesActualU]} ${anioActualU}`;
    }
    
    console.log('✅ Calendario generado completamente');
}

// Función de navegación
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
    console.log('📅 Nuevo mes:', mesActualU + 1, 'Nuevo año:', anioActualU);
    generarCalendario();
};

// Inicializar
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Inicializando calendario...');
    generarCalendario();
});