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
    } else {
        html.setAttribute('data-theme', 'dark');
        themeIcon.className = 'fas fa-sun';
        themeText.textContent = 'Modo Claro';
    }
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
        top: 20px;
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

    // Agregar estilos de animación si no existen
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
// VALIDACIÓN DEL FORMULARIO - NUEVA VERSIÓN ROBUSTA
// ============================
function validarFormulario() {
    console.log('=== INICIANDO VALIDACIÓN DEL FORMULARIO ===');
    
    try {
        const form = document.getElementById('solicitudForm');
        if (!form) {
            console.error('ERROR: Formulario no encontrado');
            return false;
        }
        
        // Validaciones básicas
        const nombreEvento = form.querySelector('[name="nombre_evento"]');
        const fechaEvento = form.querySelector('[name="fecha_evento"]');
        const tipoEspacio = form.querySelector('[name="tipo_espacio"]');

        console.log('Elementos básicos:', {
            nombreEvento: !!nombreEvento && nombreEvento.value,
            fechaEvento: !!fechaEvento && fechaEvento.value,
            tipoEspacio: !!tipoEspacio && tipoEspacio.value
        });

        if (!nombreEvento || !nombreEvento.value.trim()) {
            showAlert('El nombre del evento es obligatorio', 'error');
            if (nombreEvento) nombreEvento.focus();
            return false;
        }

        if (!fechaEvento || !fechaEvento.value) {
            showAlert('La fecha del evento es obligatoria', 'error');
            if (fechaEvento) fechaEvento.focus();
            return false;
        }

        if (!tipoEspacio || !tipoEspacio.value) {
            showAlert('Debes seleccionar un tipo de espacio', 'error');
            if (tipoEspacio) tipoEspacio.focus();
            return false;
        }

        console.log('Tipo de espacio seleccionado:', tipoEspacio.value);

        // Validación específica de espacios
        if (tipoEspacio.value === 'carrera') {
            const espacioCarreraDiv = document.getElementById('espacioCarreraDiv');
            const espacioCarrera = form.querySelector('select[name="espacio_carrera"]');
            
            console.log('Validando espacio carrera:', {
                divVisible: espacioCarreraDiv ? espacioCarreraDiv.style.display : 'div no encontrado',
                elemento: !!espacioCarrera,
                valor: espacioCarrera ? espacioCarrera.value : 'no encontrado',
                opciones: espacioCarrera ? espacioCarrera.options.length : 0
            });
            
            if (!espacioCarrera) {
                console.error('ERROR: Select de espacio_carrera no encontrado en DOM');
                showAlert('Error del sistema: campo de espacio no disponible', 'error');
                return false;
            }
            
            if (!espacioCarrera.value || espacioCarrera.value === '') {
                console.error('ERROR: Espacio de carrera no seleccionado');
                showAlert('Debes seleccionar un espacio de carrera', 'error');
                if (espacioCarrera) espacioCarrera.focus();
                return false;
            }
        }

        if (tipoEspacio.value === 'campus') {
            const espacioCampusDiv = document.getElementById('espacioCampusDiv');
            const espacioCampus = form.querySelector('select[name="espacio_campus"]');
            
            console.log('Validando espacio campus:', {
                divVisible: espacioCampusDiv ? espacioCampusDiv.style.display : 'div no encontrado',
                elemento: !!espacioCampus,
                valor: espacioCampus ? espacioCampus.value : 'no encontrado',
                opciones: espacioCampus ? espacioCampus.options.length : 0
            });
            
            if (!espacioCampus) {
                console.error('ERROR: Select de espacio_campus no encontrado en DOM');
                showAlert('Error del sistema: campo de espacio no disponible', 'error');
                return false;
            }
            
            if (!espacioCampus.value || espacioCampus.value === '') {
                console.error('ERROR: Espacio de campus no seleccionado');
                showAlert('Debes seleccionar un espacio de campus', 'error');
                if (espacioCampus) espacioCampus.focus();
                return false;
            }
        }

        console.log('=== VALIDACIÓN EXITOSA ===');
        showAlert('Validación exitosa. Enviando solicitud...', 'success');
        return true;
        
    } catch (error) {
        console.error('ERROR EN VALIDACIÓN:', error);
        showAlert('Error del sistema durante la validación', 'error');
        return false;
    }
}

// ============================
// CONFIGURACIÓN DE ESPACIOS
// ============================
function configurarEspacios() {
    console.log('CONFIGURANDO TIPO ESPACIO...');
    
    const tipoSelect = document.querySelector('select[name="tipo_espacio"]');
    if (!tipoSelect) {
        console.error('ERROR: Select tipo_espacio no encontrado');
        return;
    }

    console.log('Select encontrado:', tipoSelect);

    tipoSelect.addEventListener('change', function() {
        console.log('CAMBIO DETECTADO:', this.value);
        
        const carreraDiv = document.getElementById('espacioCarreraDiv');
        const campusDiv = document.getElementById('espacioCampusDiv');
        
        console.log('Divs encontrados:', {
            carrera: !!carreraDiv,
            campus: !!campusDiv
        });
        
        // Ocultar ambos
        if (carreraDiv) {
            carreraDiv.style.display = 'none';
            carreraDiv.style.opacity = '0';
        }
        if (campusDiv) {
            campusDiv.style.display = 'none';
            campusDiv.style.opacity = '0';
        }
        
        // Mostrar el correspondiente
        if (this.value === 'carrera' && carreraDiv) {
            console.log('MOSTRANDO CARRERA');
            carreraDiv.style.display = 'block';
            setTimeout(() => {
                carreraDiv.style.opacity = '1';
            }, 50);
        } else if (this.value === 'campus' && campusDiv) {
            console.log('MOSTRANDO CAMPUS');
            campusDiv.style.display = 'block';
            setTimeout(() => {
                campusDiv.style.opacity = '1';
            }, 50);
        }
    });
    
    console.log('EVENT LISTENER AGREGADO AL SELECT');
}

// ============================
// CONFIGURACIÓN DE FILE UPLOAD
// ============================
function configurarFileUpload() {
    console.log('CONFIGURANDO FILE UPLOAD...');
    
    const fileArea = document.getElementById('fileUploadArea');
    const fileInput = document.querySelector('input[name="archivo_adjunto"]');
    const fileInfo = document.getElementById('fileInfo');
    
    if (!fileArea || !fileInput) {
        console.error('ERROR: Elementos de file upload no encontrados');
        return;
    }

    console.log('Elementos encontrados:', { fileArea: !!fileArea, fileInput: !!fileInput });

    // Ocultar input
    fileInput.style.cssText = `
        position: absolute !important;
        left: -9999px !important;
        opacity: 0 !important;
        visibility: hidden !important;
    `;
    
    fileArea.addEventListener('click', function(e) {
        e.preventDefault();
        console.log('CLICK EN FILE AREA DETECTADO');
        fileInput.click();
    });
    
    fileInput.addEventListener('change', function() {
        console.log('ARCHIVO SELECCIONADO:', this.files[0]);
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
                    <div style="
                        display: flex;
                        align-items: center;
                        gap: 12px;
                        padding: 12px;
                        background: #f0fdf4;
                        border: 2px solid #22c55e;
                        border-radius: 8px;
                        margin-top: 8px;
                    ">
                        <i class="${iconClass}" style="font-size: 24px; color: #22c55e;"></i>
                        <div style="flex: 1;">
                            <div style="font-weight: 500; color: #1f2937;">${fileName}</div>
                            <div style="font-size: 14px; color: #6b7280;">${fileSize}</div>
                        </div>
                        <button type="button" onclick="removerArchivo()" style="
                            background: #ef4444;
                            color: white;
                            border: none;
                            border-radius: 50%;
                            width: 28px;
                            height: 28px;
                            cursor: pointer;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                        ">
                            <i class="fas fa-times" style="font-size: 12px;"></i>
                        </button>
                    </div>
                `;
                fileInfo.style.display = 'block';
            }
            
            fileArea.style.display = 'none';
            showAlert('Archivo seleccionado correctamente', 'success');
        }
    });
    
    console.log('FILE UPLOAD CONFIGURADO');
}

// ============================
// INICIALIZACIÓN COMPLETA
// ============================
console.log('=== SCRIPT DE DEBUG INICIADO ===');

// Función de inicialización que se ejecuta cuando está todo listo
function inicializarTodo() {
    console.log('=== TESTING DOM ===');
    
    const tipoSelect = document.querySelector('select[name="tipo_espacio"]');
    const fileArea = document.getElementById('fileUploadArea');
    const fileInput = document.querySelector('input[name="archivo_adjunto"]');
    
    console.log('Elementos principales:', {
        tipoSelect: !!tipoSelect,
        fileArea: !!fileArea,
        fileInput: !!fileInput
    });
    
    // Configurar espacios
    if (tipoSelect) {
        configurarEspacios();
    }
    
    // Configurar file upload
    if (fileArea && fileInput) {
        configurarFileUpload();
    }
    
    console.log('=== DEBUG COMPLETADO ===');
}

// Ejecutar inicialización cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM Content Loaded');
    setTimeout(inicializarTodo, 1000);
});

// También ejecutar si el DOM ya está cargado
if (document.readyState === 'loading') {
    console.log('DOM todavía cargando...');
} else {
    console.log('DOM ya está cargado, ejecutando inmediatamente');
    setTimeout(inicializarTodo, 500);
}

// ============================
// FUNCIONES GLOBALES
// ============================
window.toggleTheme = toggleTheme;
window.validarFormulario = validarFormulario;

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
    
    showAlert('Archivo removido correctamente', 'success');
};