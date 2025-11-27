/* ===== AISLAR TEMA POR ROL ===== */
const ROL = location.pathname.split('/')[1].replace(/\/$/, '') || 'encargado';
const THEME_KEY = `theme-${ROL}`;

(function applyOwnTheme() {
    const saved = localStorage.getItem(THEME_KEY) || 'light';
    document.body.setAttribute('data-theme', saved);
})();

function toggleTheme() {
    const body = document.body;
    const esOscuro = body.getAttribute('data-theme') === 'dark';
    const nuevo = esOscuro ? 'light' : 'dark';
    body.setAttribute('data-theme', nuevo);
    localStorage.setItem(THEME_KEY, nuevo);
}

function getCSRFToken() {
    let csrfToken = null;
    const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
    if (csrfInput) {
        csrfToken = csrfInput.value;
    }

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
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(notification => notification.remove());

    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span>${message}</span>
            <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
        </div>
    `;

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

    setTimeout(() => {
        if (notification.parentElement) {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => notification.remove(), 300);
        }
    }, 5000);
}

window.confirmarEliminar = function (solicitudId, solicitante) {
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

// ✅ CORRECCIÓN PRINCIPAL: Cambiar URL de aprobar
window.aceptarSolicitud = function(solicitudId) {
    const csrftoken = getCSRFToken();
    
    if (!csrftoken) {
        showNotification('Error: No se pudo obtener el token CSRF', 'error');
        return;
    }
    
    // ✅ URL CORREGIDA
    fetch(`/encargados/aprobar_solicitud/${solicitudId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'warning') {
            mostrarAlertaConflicto(solicitudId, data.conflictos);
        } else if (data.status === 'success') {
            if (typeof Swal !== 'undefined') {
                Swal.fire({
                    icon: 'success',
                    title: '¡Solicitud Aprobada!',
                    text: data.message,
                    confirmButtonColor: '#10b981'
                }).then(() => {
                    location.reload();
                });
            } else {
                showNotification('Solicitud aceptada correctamente', 'success');
                setTimeout(() => location.reload(), 1000);
            }
        } else {
            if (typeof Swal !== 'undefined') {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: data.message,
                    confirmButtonColor: '#ef4444'
                });
            } else {
                showNotification(data.message || 'Error al aceptar la solicitud', 'error');
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Ocurrió un error al procesar la solicitud, verifica la fecha y hora.',
                confirmButtonColor: '#ef4444'
            });
        } else {
            showNotification('Error al procesar la solicitud', 'error');
        }
    });
};

window.aprobarSolicitud = window.aceptarSolicitud;

function mostrarAlertaConflicto(solicitudId, conflictos) {
    let conflictosHTML = '<div class="text-left mt-3">';
    conflictosHTML += '<p class="font-semibold mb-2">Reservas en conflicto:</p>';
    conflictosHTML += '<ul class="list-disc pl-5 space-y-2">';
    
    conflictos.forEach(conflicto => {
        let duracionTexto = conflicto.duracion;
        if (duracionTexto % 1 === 0) {
            duracionTexto = `${duracionTexto} hora${duracionTexto !== 1 ? 's' : ''}`;
        } else {
            duracionTexto = `${duracionTexto} horas`;
        }
        
        conflictosHTML += `
            <li>
                <strong>${conflicto.nombre_evento}</strong><br>
                <span class="text-sm text-gray-600">
                    📅 ${conflicto.fecha} a las ${conflicto.hora}<br>
                    ⏱️ Duración: ${duracionTexto}<br>
                    👤 Solicitante: ${conflicto.solicitante}
                </span>
            </li>
        `;
    });
    
    conflictosHTML += '</ul></div>';
    
    Swal.fire({
        icon: 'warning',
        title: '⚠️ Conflicto de Horario',
        html: `
            <p class="mb-2">Ya existe(n) <strong>${conflictos.length}</strong> reserva(s) aceptada(s) para este espacio en el mismo horario.</p>
            ${conflictosHTML}
            <p class="mt-4 text-sm text-gray-700">
                ¿Deseas aprobar esta solicitud de todas formas?<br>
                <span class="text-red-600">Esto puede causar sobreposición de eventos.</span>
            </p>
        `,
        showCancelButton: true,
        showDenyButton: true,
        confirmButtonText: 'Aprobar de todas formas',
        denyButtonText: 'Rechazar solicitud',
        cancelButtonText: 'Cancelar',
        confirmButtonColor: '#f59e0b',
        denyButtonColor: '#ef4444',
        cancelButtonColor: '#6b7280',
        width: '600px'
    }).then((result) => {
        if (result.isConfirmed) {
            aprobarConConflicto(solicitudId);
        } else if (result.isDenied) {
            solicitarMotivoRechazo(solicitudId, 'Conflicto de horario con otra reserva aceptada.');
        }
    });
}

function aprobarConConflicto(solicitudId) {
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    fetch(`/encargados/aprobar-con-conflicto/${solicitudId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            Swal.fire({
                icon: 'success',
                title: '¡Aprobada!',
                text: data.message,
                confirmButtonColor: '#10b981'
            }).then(() => {
                location.reload();
            });
        } else {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: data.message,
                confirmButtonColor: '#ef4444'
            });
        }
    })
    .catch(error => {
        console.error('Error:', error);
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'Ocurrió un error al aprobar la solicitud.',
            confirmButtonColor: '#ef4444'
        });
    });
}

function solicitarMotivoRechazo(solicitudId, motivoPredefenido = '') {
    Swal.fire({
        title: 'Rechazar Solicitud',
        html: `
            <textarea 
                id="motivo-rechazo" 
                class="swal2-textarea w-full" 
                placeholder="Explica el motivo del rechazo..."
                rows="4"
            >${motivoPredefenido}</textarea>
        `,
        showCancelButton: true,
        confirmButtonText: 'Rechazar',
        cancelButtonText: 'Cancelar',
        confirmButtonColor: '#ef4444',
        preConfirm: () => {
            const motivo = document.getElementById('motivo-rechazo').value;
            if (!motivo.trim()) {
                Swal.showValidationMessage('Debes ingresar un motivo');
            }
            return motivo;
        }
    }).then((result) => {
        if (result.isConfirmed) {
            rechazarSolicitudDirecta(solicitudId, result.value);
        }
    });
}

// ✅ CORRECCIÓN: Nueva función con URL correcta
function rechazarSolicitudDirecta(solicitudId, motivo) {
    const csrftoken = getCSRFToken();
    
    // ✅ URL CORREGIDA
    fetch(`/encargados/rechazar_solicitud/${solicitudId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            motivo_rechazo: motivo
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            Swal.fire({
                icon: 'success',
                title: 'Solicitud Rechazada',
                text: data.message,
                confirmButtonColor: '#10b981'
            }).then(() => {
                location.reload();
            });
        } else {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: data.message,
                confirmButtonColor: '#ef4444'
            });
        }
    })
    .catch(error => {
        console.error('Error:', error);
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'Ocurrió un error al rechazar la solicitud.',
            confirmButtonColor: '#ef4444'
        });
    });
}

window.rechazarSolicitud = function (solicitudId, solicitante) {
    openRejectModal(solicitudId, solicitante);
};

window.openRejectModal = function (solicitudId, solicitanteName) {
    window.currentSolicitudId = solicitudId;
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

window.closeRejectModal = function () {
    const modal = document.getElementById('rejectModal');
    modal.querySelector('.modal').classList.remove('show');
    setTimeout(() => {
        modal.style.display = 'none';
        window.currentSolicitudId = null;
    }, 300);
};

window.confirmReject = function () {
    const reason = document.getElementById('rejectionReason').value;
    const errorMessage = document.getElementById('errorMessage');

    if (!reason.trim()) {
        document.getElementById('rejectionReason').classList.add('error');
        errorMessage.style.display = 'flex';
        return;
    }

    document.getElementById('rejectionReason').classList.remove('error');
    errorMessage.style.display = 'none';

    const csrfToken = getCSRFToken();
    if (!csrfToken) {
        showNotification('Error: No se pudo obtener el token CSRF', 'error');
        return;
    }

    fetch(`/encargados/rechazar_solicitud/${window.currentSolicitudId}/`, {
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

function initListarSolicitudes() {
    const rejectModal = document.getElementById('rejectModal');
    if (!rejectModal) return;

    rejectModal.addEventListener('click', function (e) {
        if (e.target === this) {
            closeRejectModal();
        }
    });
}

document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
        if (typeof closeRejectModal === 'function') {
            const modal = document.getElementById('rejectModal');
            if (modal && modal.style.display === 'flex') {
                closeRejectModal();
            }
        }
    }
});

document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        const modals = document.querySelectorAll('[id*="Modal"], .modal-overlay, [class*="modal"]');
        modals.forEach(modal => {
            if (modal.style.display === 'flex' || modal.style.display === 'block') {
                modal.style.display = 'none';
                const innerModal = modal.querySelector('.modal');
                if (innerModal) {
                    innerModal.classList.remove('show');
                }
            }
        });
        
        if (typeof closeRejectModal === 'function') {
            closeRejectModal();
        }
    }
});

function initSolicitudesAceptadas() {
    if (!document.querySelector('.solicitudes-aceptadas')) return;

    document.querySelectorAll('.btn-delete').forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault();
            const solicitudId = this.getAttribute('data-id');
            const solicitante = this.getAttribute('data-name') || 'este usuario';
            confirmarEliminar(solicitudId, solicitante);
        });
    });
}

function initSolicitudesPendientes() {
    if (!document.querySelector('.solicitudes-pendientes')) return;

    document.querySelectorAll('.btn-accept').forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault();
            const solicitudId = this.getAttribute('data-id');
            aceptarSolicitud(solicitudId);
        });
    });

    document.querySelectorAll('.btn-reject').forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault();
            const solicitudId = this.getAttribute('data-id');
            const solicitanteName = this.getAttribute('data-name');
            rechazarSolicitud(solicitudId, solicitanteName);
        });
    });
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
    return timeString.slice(0, 5);
}

document.addEventListener('DOMContentLoaded', function () {
    initDashboardEncargado();
    initListarSolicitudes();
    initSolicitudesAceptadas();
    initSolicitudesPendientes();

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