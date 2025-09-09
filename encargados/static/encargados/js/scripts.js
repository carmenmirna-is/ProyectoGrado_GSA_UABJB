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

// ============================
// SCRIPTS DEL DASHBOARD ENCARGADO
// ============================
function initDashboardEncargado() {
    if (!document.getElementById('calendario-body')) return;

    const hoy = new Date();
    let mesActual = hoy.getMonth();
    let anioActual = hoy.getFullYear();
    const nombresMeses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
    
    async function cargarSolicitudesAceptadas() {
    try {
        const res = await fetch('/encargados/api/solicitudes-aceptadas/');
        const data = await res.json();   // esperamos [{fecha, nombre_evento, espacio}]
        const eventosMap = {};

        data.forEach(s => {
            // fecha viene 2025-09-23 → 2025-9-23 (sin 0)
            const key = s.fecha.replace(/-0/g, '-');
            if (!eventosMap[key]) eventosMap[key] = [];
            eventosMap[key].push({
                nombre: s.nombre_evento,
                espacio: s.espacio__nombre,   // ajusta según tu modelo
                color: '#10b981'              // verde “aceptada”
            });
        });
        return eventosMap;
    } catch (err) {
        console.error('No se pudieron cargar las solicitudes aceptadas', err);
        return {};
    }
}

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
                    celda.addEventListener('click', () => mostrarModal('editar', celda.dataset.fecha));
                    fecha++;
                }
            }
        }
        document.getElementById('titulo-mes').textContent = `${nombresMeses[mesActual]} ${anioActual}`;
    }

    window.cambiarMes = function(direccion) {
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
                if (!eventos[fecha]) eventos[fecha] = [];
                if (eventos[fecha].length === 0) {
                    eventos[fecha].push({ nombre, espacio, color });
                } else {
                    eventos[fecha][0] = { nombre, espacio, color };
                }
            }
            
            cerrarModal();
            generarCalendario();
        };
    };

    window.cerrarModal = function() {
        document.getElementById('modal').style.display = 'none';
    };

    // Cerrar modal al hacer clic fuera
    window.onclick = function(event) {
        const modal = document.getElementById('modal');
        if (event.target === modal) {
            cerrarModal();
        }
    };

    // Cerrar modal con ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            cerrarModal();
        }
    });

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
        document.getElementById('rejectionReason').classList.remove('error');
        document.getElementById('errorMessage').style.display = 'none';
        
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

        // Obtener el token CSRF
        const csrfToken = getCSRFToken();
        if (!csrfToken) {
            showNotification('Error: No se pudo obtener el token CSRF', 'error');
            return;
        }

        // Enviar petición al servidor para rechazar la solicitud
        fetch(`/encargados/rechazar_solicitud/${currentSolicitudId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `motivo_rechazo=${encodeURIComponent(reason)}`
        }).then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
        }).then(data => {
            showNotification('Solicitud rechazada correctamente', 'success');
            closeRejectModal();
            setTimeout(() => location.reload(), 1000);
        }).catch(error => {
            console.error('Error:', error);
            showNotification('Error al rechazar la solicitud', 'error');
            closeRejectModal();
        });
    };

    // Función para confirmar eliminación
    window.confirmarEliminar = function(solicitudId, solicitante) {
        if (confirm(`¿Estás seguro de que deseas eliminar la solicitud de ${solicitante}?`)) {
            const csrfToken = getCSRFToken();
            if (!csrfToken) {
                showNotification('Error: No se pudo obtener el token CSRF', 'error');
                return;
            }

            fetch(`/encargados/eliminar_solicitud/${solicitudId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json'
                }
            }).then(response => {
                if (response.ok) {
                    return response.json();
                } else {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
            }).then(data => {
                showNotification('Solicitud eliminada correctamente', 'success');
                setTimeout(() => location.reload(), 1000);
            }).catch(error => {
                console.error('Error:', error);
                showNotification('Error al eliminar la solicitud', 'error');
            });
        }
    };

    // Función para aceptar solicitudes
    window.aceptarSolicitud = function(solicitudId) {
        if (confirm('¿Confirmas que deseas aceptar esta solicitud?')) {
            const csrfToken = getCSRFToken();
            if (!csrfToken) {
                showNotification('Error: No se pudo obtener el token CSRF', 'error');
                return;
            }

            fetch(`/encargados/aprobar_solicitud/${solicitudId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json'
                }
            }).then(response => {
                if (response.ok) {
                    return response.json();
                } else {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
            }).then(data => {
                showNotification('Solicitud aceptada correctamente', 'success');
                setTimeout(() => location.reload(), 1000);
            }).catch(error => {
                console.error('Error:', error);
                showNotification('Error al aceptar la solicitud', 'error');
            });
        }
    };

    // Función para rechazar solicitudes
    window.rechazarSolicitud = function(solicitudId, solicitante) {
        openRejectModal(solicitudId, solicitante);
    };

    // Cerrar modal al hacer clic fuera
    document.getElementById('rejectModal').addEventListener('click', function(e) {
        if (e.target === this) {
            closeRejectModal();
        }
    });

    // Cerrar modal con ESC
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
    
    // Funcionalidad para confirmación de eliminación
    const deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const solicitudId = this.getAttribute('data-id');
            const solicitante = this.getAttribute('data-name') || 'este usuario';
            confirmarEliminar(solicitudId, solicitante);
        });
    });
}

// ============================
// SCRIPTS DE SOLICITUDES PENDIENTES
// ============================
function initSolicitudesPendientes() {
    if (!document.querySelector('.solicitudes-pendientes')) return;
    
    // Funcionalidad para confirmación de acciones
    const acceptButtons = document.querySelectorAll('.btn-accept');
    const rejectButtons = document.querySelectorAll('.btn-reject');
    
    acceptButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const solicitudId = this.getAttribute('data-id');
            aceptarSolicitud(solicitudId);
        });
    });
    
    rejectButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const solicitudId = this.getAttribute('data-id');
            const solicitanteName = this.getAttribute('data-name');
            rechazarSolicitud(solicitudId, solicitanteName);
        });
    });
}

// ============================
// FUNCIONES UTILES
// ============================
function getCSRFToken() {
    // Buscar el token CSRF en diferentes lugares
    let csrfToken = null;
    
    // Buscar en input oculto
    const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
    if (csrfInput) {
        csrfToken = csrfInput.value;
    }
    
    // Buscar en cookies como fallback
    if (!csrfToken) {
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        csrfToken = cookieValue;
    }
    
    return csrfToken;
}

function showNotification(message, type = 'info') {
    // Eliminar notificaciones existentes
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(notification => notification.remove());
    
    // Crear notificación toast
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span>${message}</span>
            <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
        </div>
    `;
    
    // Estilos dinámicos
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--bg-primary);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 1rem;
        box-shadow: var(--shadow-lg);
        z-index: 9999;
        max-width: 300px;
        transition: all 0.3s ease;
        animation: slideIn 0.3s ease-out;
    `;
    
    // Agregar colores específicos según el tipo
    if (type === 'success') {
        notification.style.backgroundColor = '#d1fae5';
        notification.style.borderColor = '#10b981';
        notification.style.color = '#065f46';
    } else if (type === 'error') {
        notification.style.backgroundColor = '#fecaca';
        notification.style.borderColor = '#ef4444';
        notification.style.color = '#991b1b';
    }
    
    document.body.appendChild(notification);
    
    // Auto-remove después de 5 segundos
    setTimeout(() => {
        if (notification.parentElement) {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => notification.remove(), 300);
        }
    }, 5000);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
    });
}

function formatTime(timeString) {
    return timeString.slice(0, 5); // HH:MM format
}

// Abrir modal y cargar datos
document.addEventListener('click', e => {
  if (e.target.closest('.btn-editar-fecha')) {
    const btn = e.target.closest('.btn-editar-fecha');
    modalEditarFecha.showModal();
    id_solicitud_id.value = btn.dataset.id;
    id_nueva_fecha.value = btn.dataset.fecha;
    tituloEvento.textContent = btn.dataset.evento;
  }
});

// Enviar cambio vía AJAX
formEditarFecha.addEventListener('submit', async (e) => {
  e.preventDefault();
  const data = new FormData(formEditarFecha);
  const res = await fetch("{% url 'encargados:editar_fecha_aceptada' %}", {
    method: 'POST',
    headers: { 'X-CSRFToken': '{{ csrf_token }}' },
    body: data
  });
  const json = await res.json();
  alert(json.message);
  if (json.status === 'success') location.reload();
});

// ============================
// INICIALIZACIÓN
// ============================
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar todas las funciones
    initDashboardEncargado();
    initListarSolicitudes();
    initSolicitudesAceptadas();
    initSolicitudesPendientes();
    
    // Cargar tema guardado
    const savedTheme = localStorage.getItem('theme');
    const themeIcon = document.getElementById('theme-icon');
    const themeText = document.getElementById('theme-text');
    
    if (savedTheme === 'dark' && themeIcon && themeText) {
        document.documentElement.setAttribute('data-theme', 'dark');
        themeIcon.className = 'fas fa-sun';
        themeText.textContent = 'Modo Claro';
    }
    
    console.log('Sistema UABJB inicializado correctamente');
});