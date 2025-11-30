/* ===== AISLAR TEMA POR ROL ===== */
const ROL = location.pathname.split('/')[1].replace(/\/$/, '') || 'usuario';
const THEME_KEY = `theme-${ROL}`;

// Aplicar tema propio al cargar
(function applyOwnTheme() {
    const saved = localStorage.getItem(THEME_KEY) || 'light';
    document.body.setAttribute('data-theme', saved);
})();

// Sobrescribir toggleTheme() para que use clave propia
function toggleTheme() {
    const body = document.body;
    const esOscuro = body.getAttribute('data-theme') === 'dark';
    const nuevo = esOscuro ? 'light' : 'dark';
    body.setAttribute('data-theme', nuevo);
    localStorage.setItem(THEME_KEY, nuevo);
}

// ============================
// FUNCIÓN PARA MOSTRAR ALERTAS
// ============================
function showAlert(message, type = 'info') {
    const existingAlerts = document.querySelectorAll('.alert-dynamic');
    existingAlerts.forEach(alert => alert.remove());

    const alert = document.createElement('div');
    alert.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dynamic`;
    alert.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        max-width: 500px;
        padding: 15px 20px;
        border-radius: 12px;
        font-weight: 500;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        animation: slideInRight 0.3s ease-out;
    `;

    const styles = {
        success: { bg: 'rgba(76, 201, 240, 0.1)', border: '#4cc9f0', color: '#4cc9f0' },
        error: { bg: 'rgba(220, 38, 38, 0.1)', border: '#dc2626', color: '#dc2626' },
        warning: { bg: 'rgba(251, 191, 36, 0.1)', border: '#fbbf24', color: '#fbbf24' },
        info: { bg: 'rgba(67, 97, 238, 0.1)', border: '#4361ee', color: '#4361ee' }
    };

    const style = styles[type] || styles.info;
    alert.style.background = style.bg;
    alert.style.borderLeft = `4px solid ${style.border}`;
    alert.style.color = style.color;

    alert.innerHTML = `
        <div style="display: flex; align-items: center; gap: 10px;">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-triangle' : 'info-circle'}"></i>
            <span>${message}</span>
            <button type="button" onclick="this.parentElement.parentElement.remove()" 
                style="background: none; border: none; color: inherit; cursor: pointer; font-size: 18px; margin-left: auto;">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;

    document.body.appendChild(alert);

    if (!document.getElementById('alert-styles')) {
        const alertStyles = document.createElement('style');
        alertStyles.id = 'alert-styles';
        alertStyles.textContent = `
            @keyframes slideInRight {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideOutRight {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(100%); opacity: 0; }
            }
        `;
        document.head.appendChild(alertStyles);
    }

    setTimeout(() => {
        if (alert.parentElement) {
            alert.style.animation = 'slideOutRight 0.3s ease-in forwards';
            setTimeout(() => alert.remove(), 300);
        }
    }, 5000);
}

// ============================
// VALIDACIÓN DEL FORMULARIO
// ============================
function validarFormulario() {
    const form = document.getElementById('solicitudForm');
    if (!form) return false;
    
    const nombreEvento = form.querySelector('[name="nombre_evento"]');
    const fechaEvento = form.querySelector('[name="fecha_evento"]');
    const tipoEspacio = form.querySelector('[name="tipo_espacio"]');
    const archivoAdjunto = form.querySelector('[name="archivo_adjunto"]');

    // ✅ Validar nombre del evento
    if (!nombreEvento || !nombreEvento.value.trim()) {
        showAlert('El nombre del evento es obligatorio', 'error');
        if (nombreEvento) nombreEvento.focus();
        return false;
    }

    // ✅ Validar fecha
    if (!fechaEvento || !fechaEvento.value) {
        showAlert('La fecha del evento es obligatoria', 'error');
        if (fechaEvento) fechaEvento.focus();
        return false;
    }

    // ✅ Validar tipo de espacio
    if (!tipoEspacio || !tipoEspacio.value) {
        showAlert('Debes seleccionar un tipo de espacio', 'error');
        if (tipoEspacio) tipoEspacio.focus();
        return false;
    }

    // ✅ Validar espacio según tipo
    if (tipoEspacio.value === 'carrera') {
        const espacioCarrera = form.querySelector('select[name="espacio_carrera"]');
        if (!espacioCarrera || !espacioCarrera.value) {
            showAlert('Debes seleccionar un espacio de carrera', 'error');
            if (espacioCarrera) espacioCarrera.focus();
            return false;
        }
    } else if (tipoEspacio.value === 'campus') {
        const espacioCampus = form.querySelector('select[name="espacio_campus"]');
        if (!espacioCampus || !espacioCampus.value) {
            showAlert('Debes seleccionar un espacio de campus', 'error');
            if (espacioCampus) espacioCampus.focus();
            return false;
        }
        
        // ✅ Validar aceptación de condiciones para campus
        const aceptaCondiciones = form.querySelector('[name="acepta_condiciones_uso"]');
        if (aceptaCondiciones && !aceptaCondiciones.checked) {
            showAlert('Debes aceptar las condiciones de uso para espacios de campus', 'error');
            aceptaCondiciones.focus();
            return false;
        }
    }

    // ✅ Validar archivo adjunto
    if (!archivoAdjunto || !archivoAdjunto.files || archivoAdjunto.files.length === 0) {
        showAlert('Debes adjuntar un archivo con la justificación', 'error');
        return false;
    }

    return true;
}

// ============================
// CONFIGURACIÓN DE ESPACIOS
// ============================
function configurarEspacios() {
    const tipoSelect = document.querySelector('select[name="tipo_espacio"]');
    if (!tipoSelect) return;

    tipoSelect.addEventListener('change', function() {
        const carreraDiv = document.getElementById('espacioCarreraDiv');
        const campusDiv = document.getElementById('espacioCampusDiv');
        const terminosSection = document.getElementById('terminosSection');
        
        // Ocultar todo
        if (carreraDiv) {
            carreraDiv.style.display = 'none';
            carreraDiv.style.opacity = '0';
        }
        if (campusDiv) {
            campusDiv.style.display = 'none';
            campusDiv.style.opacity = '0';
        }
        if (terminosSection) {
            terminosSection.classList.remove('visible');
        }
        
        // Mostrar según selección
        if (this.value === 'carrera' && carreraDiv) {
            carreraDiv.style.display = 'block';
            setTimeout(() => carreraDiv.style.opacity = '1', 50);
        } else if (this.value === 'campus' && campusDiv) {
            campusDiv.style.display = 'block';
            setTimeout(() => campusDiv.style.opacity = '1', 50);
        }
    });
}

// ============================
// CONFIGURACIÓN DE FILE UPLOAD
// ============================
function configurarFileUpload() {
    const fileArea = document.getElementById('fileUploadArea');
    const fileInput = document.querySelector('input[name="archivo_adjunto"]');
    const fileInfo = document.getElementById('fileInfo');
    
    if (!fileArea || !fileInput) return;

    // Ocultar input original
    fileInput.style.cssText = 'position: absolute; left: -9999px; opacity: 0; visibility: hidden;';
    
    // Click en área para abrir selector
    fileArea.addEventListener('click', function(e) {
        e.preventDefault();
        fileInput.click();
    });
    
    // Mostrar archivo seleccionado
    fileInput.addEventListener('change', function() {
        if (this.files[0]) {
            const file = this.files[0];
            const fileName = file.name;
            const fileSize = (file.size / 1024 / 1024).toFixed(2) + ' MB';
            
            let iconClass = 'fas fa-file';
            const extension = fileName.split('.').pop().toLowerCase();
            if (['jpg', 'jpeg', 'png', 'gif'].includes(extension)) {
                iconClass = 'fas fa-file-image';
            } else if (extension === 'pdf') {
                iconClass = 'fas fa-file-pdf';
            } else if (['doc', 'docx'].includes(extension)) {
                iconClass = 'fas fa-file-word';
            }
            
            if (fileInfo) {
                fileInfo.innerHTML = `
                    <div style="display: flex; align-items: center; gap: 12px; padding: 12px; background: #f0fdf4; border: 2px solid #22c55e; border-radius: 8px; margin-top: 8px;">
                        <i class="${iconClass}" style="font-size: 24px; color: #22c55e;"></i>
                        <div style="flex: 1;">
                            <div style="font-weight: 500; color: #1f2937;">${fileName}</div>
                            <div style="font-size: 14px; color: #6b7280;">${fileSize}</div>
                        </div>
                        <button type="button" onclick="removerArchivo()" style="background: #ef4444; color: white; border: none; border-radius: 50%; width: 28px; height: 28px; cursor: pointer; display: flex; align-items: center; justify-content: center;">
                            <i class="fas fa-times" style="font-size: 12px;"></i>
                        </button>
                    </div>
                `;
                fileInfo.style.display = 'block';
            }
            
            fileArea.style.display = 'none';
        }
    });
}

// ============================
// MANEJO DE TÉRMINOS PARA CAMPUS
// ============================
function verificarEspacioCampus(espacioId) {
    const terminosSection = document.getElementById('terminosSection');
    const aceptaCondiciones = document.getElementById('acepta_condiciones');
    
    if (espacioId) {
        if (terminosSection) {
            setTimeout(() => terminosSection.classList.add('visible'), 100);
        }
        if (aceptaCondiciones) {
            aceptaCondiciones.required = true;
        }
    } else {
        if (terminosSection) {
            terminosSection.classList.remove('visible');
        }
        if (aceptaCondiciones) {
            aceptaCondiciones.required = false;
            aceptaCondiciones.checked = false;
        }
    }
}

// ============================
// DESHABILITAR AUTOCOMPLETADO
// ============================
function deshabilitarAutocompletado() {
    const inputs = document.querySelectorAll('input[type="text"], textarea');
    inputs.forEach(input => {
        input.setAttribute('autocomplete', 'off');
    });
}

// ============================
// INICIALIZACIÓN
// ============================
function inicializarTodo() {
    configurarEspacios();
    configurarFileUpload();
    deshabilitarAutocompletado();
    
    // Ocultar todo al inicio
    const terminosSection = document.getElementById('terminosSection');
    const carreraDiv = document.getElementById('espacioCarreraDiv');
    const campusDiv = document.getElementById('espacioCampusDiv');
    
    if (terminosSection) terminosSection.classList.remove('visible');
    if (carreraDiv) carreraDiv.style.display = 'none';
    if (campusDiv) campusDiv.style.display = 'none';
}

// ⚡ EJECUCIÓN INMEDIATA (sin delays)
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', inicializarTodo);
} else {
    inicializarTodo();
}

// ============================
// FUNCIONES GLOBALES
// ============================
window.toggleTheme = toggleTheme;
window.validarFormulario = validarFormulario;
window.verificarEspacioCampus = verificarEspacioCampus;

window.removerArchivo = function() {
    const fileInput = document.querySelector('input[name="archivo_adjunto"]');
    const fileInfo = document.getElementById('fileInfo');
    const fileArea = document.getElementById('fileUploadArea');
    
    if (fileInput) fileInput.value = '';
    if (fileInfo) {
        fileInfo.style.display = 'none';
        fileInfo.innerHTML = '';
    }
    if (fileArea) fileArea.style.display = 'block';
};