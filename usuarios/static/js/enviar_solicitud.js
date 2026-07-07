// ============================
// TEMA Y ALERTAS
// ============================
function toggleTheme() {
  const html = document.documentElement;
  const icon = document.getElementById('theme-icon');
  const text = document.getElementById('theme-text');
  const dark = html.getAttribute('data-theme') === 'dark';
  html.setAttribute('data-theme', dark ? 'light' : 'dark');
  icon.className  = dark ? 'fas fa-moon' : 'fas fa-sun';
  text.textContent = dark ? 'Modo Oscuro' : 'Modo Claro';
}

// ============================
// MOSTRAR/OCULTAR ESPACIOS CON ANIMACIÓN
// ============================
function toggleEspacios(tipo) {
  const carrera = document.getElementById('espacioCarreraDiv');
  const campus = document.getElementById('espacioCampusDiv');
  
  if (!carrera || !campus) return;

  // Ocultar ambos primero
  carrera.style.display = 'none';
  carrera.style.opacity = '0';
  campus.style.display = 'none';
  campus.style.opacity = '0';

  // Mostrar el seleccionado con animación
  if (tipo === 'carrera') {
    carrera.style.display = 'block';
    // Forzar reflow para activar animación
    void carrera.offsetWidth;
    carrera.style.opacity = '1';
  } else if (tipo === 'campus') {
    campus.style.display = 'block';
    // Forzar reflow para activar animación
    void campus.offsetWidth;
    campus.style.opacity = '1';
  }
}

// ============================
// SISTEMA DE ALERTAS
// ============================
function mostrarAlertaExito(mensaje) {
  const alerta = document.createElement('div');
  alerta.className = 'alert alert-success';
  alerta.style.opacity = '0';
  alerta.innerHTML = `
    <i class="fas fa-check-circle"></i>
    <span>${mensaje}</span>
  `;
  
  const form = document.getElementById('solicitudForm');
  form.insertBefore(alerta, form.firstChild);
  
  // Animar entrada
  setTimeout(() => {
    alerta.style.opacity = '1';
  }, 10);
  
  // Scroll suave hacia la alerta
  alerta.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  
  // Auto-ocultar después de 5 segundos
  setTimeout(() => {
    alerta.style.opacity = '0';
    setTimeout(() => alerta.remove(), 300);
  }, 5000);
}

function mostrarAlertaError(mensaje) {
  const alerta = document.createElement('div');
  alerta.className = 'alert alert-error';
  alerta.style.opacity = '0';
  alerta.innerHTML = `
    <i class="fas fa-exclamation-circle"></i>
    <span>${mensaje}</span>
  `;
  
  const form = document.getElementById('solicitudForm');
  form.insertBefore(alerta, form.firstChild);
  
  // Animar entrada
  setTimeout(() => {
    alerta.style.opacity = '1';
  }, 10);
  
  // Scroll suave hacia la alerta
  alerta.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  
  // Auto-ocultar después de 5 segundos
  setTimeout(() => {
    alerta.style.opacity = '0';
    setTimeout(() => alerta.remove(), 300);
  }, 5000);
}

function mostrarAlertaAdvertencia(mensaje) {
  const alerta = document.createElement('div');
  alerta.className = 'alert alert-warning';
  alerta.style.opacity = '0';
  alerta.innerHTML = `
    <i class="fas fa-exclamation-triangle"></i>
    <span>${mensaje}</span>
  `;
  
  const form = document.getElementById('solicitudForm');
  form.insertBefore(alerta, form.firstChild);
  
  // Animar entrada
  setTimeout(() => {
    alerta.style.opacity = '1';
  }, 10);
  
  // Scroll suave hacia la alerta
  alerta.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  
  // Auto-ocultar después de 4 segundos
  setTimeout(() => {
    alerta.style.opacity = '0';
    setTimeout(() => alerta.remove(), 300);
  }, 4000);
}

// ============================
// SISTEMA DE CARGA DE ARCHIVOS
// ============================
function initFileUpload() {
  const fileInput = document.getElementById('archivo_adjunto');
  const uploadArea = document.querySelector('.file-upload-area');
  const fileInfo = document.getElementById('fileInfo');
  
  if (!fileInput || !uploadArea) return;

  // Manejar selección de archivo
  fileInput.addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
      showFileInfo(file);
    }
  });

  // Manejar drag & drop
  uploadArea.addEventListener('dragover', function(e) {
    e.preventDefault();
    uploadArea.classList.add('dragover');
  });

  uploadArea.addEventListener('dragleave', function(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
  });

  uploadArea.addEventListener('drop', function(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      const file = files[0];
      // Validar tipo de archivo
      const validTypes = ['.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx'];
      const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
      
      if (validTypes.includes(fileExtension)) {
        fileInput.files = files;
        showFileInfo(file);
      } else {
        mostrarAlertaAdvertencia('Tipo de archivo no válido. Formatos permitidos: PDF, JPG, PNG, DOC, DOCX');
      }
    }
  });
}

// Mostrar información del archivo seleccionado
function showFileInfo(file) {
  const fileInfo = document.getElementById('fileInfo');
  const fileName = document.getElementById('fileName');
  const fileSize = document.getElementById('fileSize');
  const fileIcon = document.querySelector('.file-icon i');
  
  if (!fileInfo || !fileName || !fileSize) return;

  // Determinar icono según tipo de archivo
  const extension = file.name.split('.').pop().toLowerCase();
  let iconClass = 'fas fa-file';
  
  switch(extension) {
    case 'pdf':
      iconClass = 'fas fa-file-pdf';
      break;
    case 'jpg':
    case 'jpeg':
    case 'png':
      iconClass = 'fas fa-file-image';
      break;
    case 'doc':
    case 'docx':
      iconClass = 'fas fa-file-word';
      break;
    default:
      iconClass = 'fas fa-file';
  }
  
  fileIcon.className = iconClass;
  fileName.textContent = file.name;
  fileSize.textContent = formatFileSize(file.size);
  fileInfo.style.display = 'block';
}

// Formatear tamaño de archivo
function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Remover archivo seleccionado
function removeFile() {
  const fileInput = document.getElementById('archivo_adjunto');
  const fileInfo = document.getElementById('fileInfo');
  
  if (fileInput) {
    fileInput.value = '';
  }
  if (fileInfo) {
    fileInfo.style.display = 'none';
  }
}

// ============================
// VALIDACIÓN MEJORADA
// ============================
function validarFormulario() {
  const form = document.getElementById('solicitudForm');
  const nombre = form.querySelector('[name="nombre_evento"]').value.trim();
  const fecha  = form.querySelector('[name="fecha_evento"]').value;
  const tipo   = form.querySelector('[name="tipo_espacio"]').value;
  const carrera = form.querySelector('[name="espacio_carrera"]').value;
  const campus  = form.querySelector('[name="espacio_campus"]').value;
  const archivo = form.querySelector('[name="archivo_adjunto"]').files.length;

  if (!nombre) { 
    mostrarAlertaAdvertencia('El nombre del evento es obligatorio'); 
    return false; 
  }
  if (!fecha) { 
    mostrarAlertaAdvertencia('La fecha del evento es obligatoria'); 
    return false; 
  }
  if (!tipo) { 
    mostrarAlertaAdvertencia('Debes seleccionar el tipo de espacio'); 
    return false; 
  }
  if (tipo === 'carrera' && !carrera) { 
    mostrarAlertaAdvertencia('Debes seleccionar un espacio de carrera'); 
    return false; 
  }
  if (tipo === 'campus' && !campus) { 
    mostrarAlertaAdvertencia('Debes seleccionar un espacio de campus'); 
    return false; 
  }
  if (!archivo) { 
    mostrarAlertaAdvertencia('Debes adjuntar un archivo'); 
    return false; 
  }
  return true;
}

// ============================
// ENVÍO DEL FORMULARIO CON AJAX
// ============================
function initFormSubmit() {
  const form = document.getElementById('solicitudForm');
  if (!form) return;

  form.addEventListener('submit', async function(e) {
    e.preventDefault(); // Prevenir recarga de página
    
    // Validar formulario
    if (!validarFormulario()) return;
    
    // Obtener botón de envío
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    
    // Deshabilitar botón y mostrar loading
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Enviando...';
    
    try {
      // Crear FormData con todos los datos del formulario
      const formData = new FormData(form);
      
      // Enviar formulario
      const response = await fetch(form.action || window.location.href, {
        method: 'POST',
        body: formData
      });
      
      if (response.ok) {
        // Mostrar mensaje de éxito
        mostrarAlertaExito('¡Solicitud enviada con éxito! Redirigiendo al historial...');
        
        // Resetear formulario
        form.reset();
        removeFile();
        
        // Ocultar secciones de espacios
        const carreraDiv = document.getElementById('espacioCarreraDiv');
        const campusDiv = document.getElementById('espacioCampusDiv');
        if (carreraDiv) carreraDiv.style.display = 'none';
        if (campusDiv) campusDiv.style.display = 'none';
        
        // Redirigir al historial después de 2 segundos
        setTimeout(() => {
          window.location.href = '/usuarios/historial/';
        }, 2000);
        
      } else {
        // Error del servidor
        const errorText = await response.text();
        console.error('Error del servidor:', errorText);
        mostrarAlertaError('Hubo un error al enviar la solicitud. Por favor, intenta de nuevo.');
      }
      
    } catch (error) {
      // Error de conexión
      console.error('Error de conexión:', error);
      mostrarAlertaError('Error de conexión. Verifica tu internet e intenta de nuevo.');
      
    } finally {
      // Restaurar botón
      submitBtn.disabled = false;
      submitBtn.innerHTML = originalText;
    }
  });
}

// ============================
// INICIALIZAR
// ============================
document.addEventListener('DOMContentLoaded', () => {
  // Inicializar toggle de espacios
  const tipo = document.querySelector('select[name="tipo_espacio"]');
  if (tipo) {
    tipo.addEventListener('change', () => toggleEspacios(tipo.value));
  }
  
  // Inicializar sistema de carga de archivos
  initFileUpload();
  
  // Inicializar envío del formulario con AJAX
  initFormSubmit();
});