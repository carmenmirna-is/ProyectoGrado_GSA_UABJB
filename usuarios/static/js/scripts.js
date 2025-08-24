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
// SCRIPTS DEL DASHBOARD
// ============================
function initDashboard() {
    if (!document.getElementById('calendario-body')) return;

    // Variables globales
    let mesActual = 6; // Julio (0-11)
    let anioActual = 2025;
    const hoy = new Date();

    // Nombres de los meses
    const nombresMeses = [
        'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ];

    // Eventos de ejemplo
    const eventos = {
        '2025-7-15': [
            { nombre: 'Reunión Académica', espacio: 'Aula 101', color: '#1e3a8a' },
            { nombre: 'Presentación', espacio: 'Auditorio', color: '#fbbf24' }
        ],
        '2025-7-22': [
            { nombre: 'Examen Final', espacio: 'Aula 205', color: '#dc2626' }
        ],
        '2025-7-27': [
            { nombre: 'Evento Especial', espacio: 'Patio Central', color: '#4cc9f0' }
        ],
        '2025-7-30': [
            { nombre: 'Clase Magistral', espacio: 'Aula Magna', color: '#fbbf24' }
        ]
    };

    // Función para generar el calendario
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
                    const esDiaActual = (
                        fecha === hoy.getDate() && 
                        mesActual === hoy.getMonth() && 
                        anioActual === hoy.getFullYear()
                    );
                    
                    if (esDiaActual) {
                        celda.classList.add('dia-actual');
                    }
                    
                    const numeroDia = document.createElement('div');
                    numeroDia.className = 'numero-dia';
                    numeroDia.textContent = fecha;
                    
                    const fechaKey = `${anioActual}-${mesActual + 1}-${fecha}`;
                    const eventosDelDia = eventos[fechaKey];
                    
                    if (eventosDelDia) {
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
                    fecha++;
                }
            }
        }
        
        document.getElementById('titulo-mes').textContent = `${nombresMeses[mesActual]} ${anioActual}`;
    }

    // Función para cambiar mes
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

    // Inicializar el calendario
    generarCalendario();
}

// ============================
// SCRIPTS DE LISTAR ESPACIOS
// ============================
function initListarEspacios() {
    if (!document.querySelector('table')) return;

    const rows = document.querySelectorAll('tbody tr');
    rows.forEach((row, index) => {
        row.style.opacity = '0';
        row.style.transform = 'translateY(20px)';
        setTimeout(() => {
            row.style.transition = 'all 0.6s ease';
            row.style.opacity = '1';
            row.style.transform = 'translateY(0)';
        }, (index + 1) * 100);
    });

    document.querySelectorAll('tbody tr').forEach(row => {
        row.addEventListener('mouseenter', function() {
            this.style.boxShadow = '0 4px 12px rgba(30, 58, 138, 0.15)';
        });
        row.addEventListener('mouseleave', function() {
            this.style.boxShadow = 'none';
        });
    });
}

// ============================
// SCRIPTS DE ENVIAR SOLICITUD
// ============================
function initEnviarSolicitud() {
    if (!document.getElementById('archivo_adjunto')) return;

    function validarFecha() {
        const fechaInput = document.getElementById('fecha');
        const fechaSeleccionada = new Date(fechaInput.value);
        const fechaActual = new Date();
        
        if (fechaSeleccionada < fechaActual) {
            alert('⚠️ La fecha no puede ser en el pasado.');
            fechaInput.focus();
            return false;
        }
        
        return true;
    }

    // Manejo de archivos
    const fileInput = document.getElementById('archivo_adjunto');
    const fileUploadArea = document.querySelector('.file-upload-area');
    const fileInfo = document.getElementById('file-info');
    const fileName = document.getElementById('file-name');
    const fileSize = document.getElementById('file-size');

    fileInput.addEventListener('change', function(e) {
        handleFileSelect(e.target.files[0]);
    });

    fileUploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        this.classList.add('dragover');
    });

    fileUploadArea.addEventListener('dragleave', function(e) {
        e.preventDefault();
        this.classList.remove('dragover');
    });

    fileUploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        this.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileSelect(files[0]);
            fileInput.files = files;
        }
    });

    function handleFileSelect(file) {
        if (file) {
            const allowedTypes = [
                'image/jpeg', 'image/jpg', 'image/png', 'image/gif', 
                'application/pdf', 'application/msword', 
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            ];
            
            if (!allowedTypes.includes(file.type)) {
                alert('❌ Tipo de archivo no permitido. Solo se permiten imágenes (JPG, PNG, GIF) y documentos (PDF, DOC, DOCX).');
                return;
            }
            
            if (file.size > 10 * 1024 * 1024) {
                alert('❌ El archivo es demasiado grande. El tamaño máximo permitido es 10MB.');
                return;
            }

            fileName.textContent = file.name;
            fileSize.textContent = formatFileSize(file.size);
            
            const fileIcon = document.querySelector('.file-icon');
            if (file.type.startsWith('image/')) {
                fileIcon.className = 'fas fa-image file-icon';
            } else if (file.type === 'application/pdf') {
                fileIcon.className = 'fas fa-file-pdf file-icon';
            } else {
                fileIcon.className = 'fas fa-file-word file-icon';
            }
            
            fileUploadArea.style.display = 'none';
            fileInfo.style.display = 'block';
        }
    }

    window.removeFile = function() {
        fileInput.value = '';
        fileInfo.style.display = 'none';
        fileUploadArea.style.display = 'block';
    };

    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // Efectos de hover en inputs
    document.querySelectorAll('input, select').forEach(element => {
        element.addEventListener('focus', function() {
            this.parentElement.style.transform = 'translateY(-2px)';
        });
        
        element.addEventListener('blur', function() {
            this.parentElement.style.transform = 'translateY(0)';
        });
    });

    // Validación en tiempo real
    document.getElementById('nombre_evento').addEventListener('input', function() {
        if (this.value.length < 3) {
            this.setCustomValidity('El nombre del evento debe tener al menos 3 caracteres');
        } else {
            this.setCustomValidity('');
        }
    });

    // Exponer validarFecha globalmente
    window.validarFecha = validarFecha;
}

// ============================
// INICIALIZACIÓN
// ============================
document.addEventListener('DOMContentLoaded', function() {
    initDashboard();
    initListarEspacios();
    initEnviarSolicitud();
});