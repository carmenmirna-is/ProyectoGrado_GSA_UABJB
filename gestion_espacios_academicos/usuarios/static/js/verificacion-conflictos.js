/* ============================
   VERIFICACIÓN DE CONFLICTOS DE HORARIO
   Archivo completamente independiente
   FIX: CSRF Token mejorado
   ============================ */

(function() {
    'use strict';
    
    console.log('🚀 Cargando módulo de verificación de conflictos...');

    // Función mejorada para obtener el token CSRF
    function getCookie(name) {
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
        return cookieValue;
    }

    // Obtener CSRF token del DOM (alternativa más confiable)
    function getCSRFToken() {
        // Método 1: Desde cookie
        let token = getCookie('csrftoken');
        
        if (!token) {
            // Método 2: Desde input hidden en el formulario
            const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
            if (csrfInput) {
                token = csrfInput.value;
            }
        }
        
        if (!token) {
            // Método 3: Desde meta tag
            const csrfMeta = document.querySelector('meta[name="csrf-token"]');
            if (csrfMeta) {
                token = csrfMeta.content;
            }
        }
        
        console.log('🔑 CSRF Token obtenido:', token ? 'SÍ ✓' : 'NO ✗');
        return token;
    }

    // Función para enviar el formulario sin validación adicional
    function enviarFormularioDirectamente(form) {
        console.log('📤 Enviando formulario sin validación adicional...');
        
        // Desactivar temporalmente nuestro listener
        form.dataset.verificacionActiva = 'false';
        
        // Enviar el formulario de forma nativa
        form.submit();
    }

    // Mostrar modal de conflictos
    function mostrarModalConflictos(result, form) {
        console.log('🚨 Mostrando modal de conflictos...');
        
        const conflictos = result.conflictos || [];
        
        // Remover modal anterior si existe
        const modalAnterior = document.getElementById('modal-conflictos-overlay');
        if (modalAnterior) {
            modalAnterior.remove();
        }
        
        // Crear el modal
        const modal = document.createElement('div');
        modal.id = 'modal-conflictos-overlay';
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 999999;
            animation: fadeIn 0.3s ease;
        `;
        
        // Generar HTML de conflictos
        let conflictosHTML = '';
        conflictos.forEach((conflicto, index) => {
            const esPropio = conflicto.es_propio;
            const bgColor = esPropio ? '#fef3c7' : '#fee2e2';
            const borderColor = esPropio ? '#f59e0b' : '#ef4444';
            const icono = esPropio ? '⚠️' : '🔴';
            const etiqueta = esPropio ? 'TU RESERVA EXISTENTE' : 'RESERVA DE OTRO USUARIO';
            
            conflictosHTML += `
                <div style="
                    background: ${bgColor};
                    border-left: 4px solid ${borderColor};
                    padding: 15px;
                    margin-bottom: 12px;
                    border-radius: 8px;
                ">
                    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                        <span style="font-size: 24px;">${icono}</span>
                        <strong style="color: ${borderColor}; font-size: 14px;">${etiqueta}</strong>
                    </div>
                    <div style="font-size: 14px; color: #374151; line-height: 1.6;">
                        <div style="margin-bottom: 5px;">
                            <strong style="font-size: 15px;">📅 ${conflicto.nombre_evento}</strong>
                        </div>
                        <div style="opacity: 0.9;">
                            👤 <strong>Solicitante:</strong> ${conflicto.solicitante}
                        </div>
                        <div style="opacity: 0.9;">
                            🕒 <strong>Desde:</strong> ${conflicto.fecha_inicio}
                        </div>
                        <div style="opacity: 0.9;">
                            🕒 <strong>Hasta:</strong> ${conflicto.fecha_fin}
                        </div>
                    </div>
                </div>
            `;
        });
        
        modal.innerHTML = `
            <style>
                @keyframes fadeIn {
                    from { opacity: 0; }
                    to { opacity: 1; }
                }
                @keyframes scaleIn {
                    from { 
                        opacity: 0; 
                        transform: scale(0.9);
                    }
                    to { 
                        opacity: 1; 
                        transform: scale(1);
                    }
                }
            </style>
            <div style="
                background: white;
                border-radius: 16px;
                padding: 30px;
                max-width: 650px;
                width: 90%;
                max-height: 85vh;
                overflow-y: auto;
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
                animation: scaleIn 0.3s ease;
            ">
                <div style="text-align: center; margin-bottom: 25px;">
                    <div style="font-size: 64px; margin-bottom: 15px;">⚠️</div>
                    <h2 style="
                        margin: 0; 
                        color: #dc2626; 
                        font-size: 26px;
                        font-weight: 700;
                        margin-bottom: 8px;
                    ">
                        Conflicto de Horario Detectado
                    </h2>
                    <p style="color: #6b7280; margin: 0; font-size: 15px;">
                        Existen <strong style="color: #dc2626;">${conflictos.length}</strong> reserva(s) aceptada(s) en este horario
                    </p>
                </div>
                
                <div style="margin: 25px 0;">
                    <div style="
                        background: #f8fafc;
                        padding: 12px 16px;
                        border-radius: 8px;
                        margin-bottom: 15px;
                        border-left: 3px solid #3b82f6;
                    ">
                        <strong style="color: #1e40af;">📋 Reservas Existentes:</strong>
                    </div>
                    ${conflictosHTML}
                </div>
                
                <div style="
                    background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
                    padding: 18px;
                    border-radius: 10px;
                    margin: 20px 0;
                    font-size: 14px;
                    color: #78350f;
                    border: 2px solid #fbbf24;
                    box-shadow: 0 2px 8px rgba(251, 191, 36, 0.2);
                ">
                    <div style="display: flex; gap: 12px; align-items: start;">
                        <div style="font-size: 24px; line-height: 1;">⚠️</div>
                        <div>
                            <strong style="display: block; margin-bottom: 8px; font-size: 15px;">
                                IMPORTANTE - LEE ESTO:
                            </strong>
                            <ul style="margin: 0; padding-left: 20px; line-height: 1.8;">
                                <li>Si continúas, tu solicitud será enviada como <strong>PENDIENTE</strong></li>
                                <li>El encargado verá que existe un conflicto de horario</li>
                                <li>Es muy probable que <strong>rechacen tu solicitud</strong></li>
                                <li><strong>Recomendación:</strong> Elige otro horario disponible</li>
                            </ul>
                        </div>
                    </div>
                </div>
                
                <div style="
                    display: flex;
                    gap: 15px;
                    justify-content: center;
                    margin-top: 30px;
                    flex-wrap: wrap;
                ">
                    <button 
                        id="btn-cancelar-conflicto"
                        style="
                            padding: 14px 32px;
                            background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
                            color: white;
                            border: none;
                            border-radius: 10px;
                            cursor: pointer;
                            font-size: 16px;
                            font-weight: 600;
                            transition: all 0.3s;
                            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                        "
                    >
                        <i class="fas fa-times-circle"></i> Cancelar y Modificar
                    </button>
                    
                    <button 
                        id="btn-continuar-conflicto"
                        style="
                            padding: 14px 32px;
                            background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
                            color: white;
                            border: none;
                            border-radius: 10px;
                            cursor: pointer;
                            font-size: 16px;
                            font-weight: 600;
                            transition: all 0.3s;
                            box-shadow: 0 4px 12px rgba(220, 38, 38, 0.3);
                        "
                    >
                        <i class="fas fa-exclamation-triangle"></i> Enviar de Todos Modos
                    </button>
                </div>
                
                <div style="
                    text-align: center;
                    margin-top: 20px;
                    font-size: 13px;
                    color: #9ca3af;
                ">
                    <i class="fas fa-info-circle"></i> Presiona <kbd>ESC</kbd> para cerrar
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        console.log('✅ Modal agregado al DOM');
        
        // Event listeners para los botones
        document.getElementById('btn-cancelar-conflicto').addEventListener('click', () => {
            console.log('❌ Usuario canceló el envío');
            modal.remove();
        });
        
        document.getElementById('btn-continuar-conflicto').addEventListener('click', () => {
            console.log('⚠️ Usuario decidió enviar de todos modos');
            modal.remove();
            enviarFormularioDirectamente(form);
        });
        
        // Cerrar con ESC
        const closeOnEsc = (e) => {
            if (e.key === 'Escape') {
                modal.remove();
                document.removeEventListener('keydown', closeOnEsc);
            }
        };
        document.addEventListener('keydown', closeOnEsc);
        
        // Cerrar al hacer clic fuera
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    }

    // Verificar conflictos antes de enviar
    async function verificarConflictos(form) {
        console.log('🔍 Iniciando verificación de conflictos...');
        
        try {
            // Obtener datos del formulario
            const formData = new FormData(form);
            const fechaEvento = formData.get('fecha_evento');
            const fechaFinEvento = formData.get('fecha_fin_evento');
            const tipoEspacio = formData.get('tipo_espacio');
            const espacioCarrera = formData.get('espacio_carrera');
            const espacioCampus = formData.get('espacio_campus');
            
            console.log('📝 Datos extraídos:', {
                fechaEvento,
                fechaFinEvento,
                tipoEspacio,
                espacioCarrera,
                espacioCampus
            });
            
            // Validar datos básicos
            if (!fechaEvento || !tipoEspacio) {
                console.log('⚠️ Faltan datos básicos');
                return { continuar: true };
            }
            
            if (tipoEspacio === 'carrera' && !espacioCarrera) {
                console.log('⚠️ No hay espacio de carrera');
                return { continuar: true };
            }
            
            if (tipoEspacio === 'campus' && !espacioCampus) {
                console.log('⚠️ No hay espacio de campus');
                return { continuar: true };
            }
            
            // Preparar datos para enviar
            const data = {
                fecha_evento: fechaEvento,
                fecha_fin_evento: fechaFinEvento || '',
                tipo_espacio: tipoEspacio,
                espacio_carrera: espacioCarrera || '',
                espacio_campus: espacioCampus || ''
            };
            
            console.log('📤 Enviando petición de verificación...');
            
            // Obtener CSRF token
            const csrftoken = getCSRFToken();
            
            if (!csrftoken) {
                console.error('❌ No se pudo obtener el CSRF token');
                return { continuar: true };
            }
            
            // Hacer la petición
            const response = await fetch('/usuarios/verificar-conflictos/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken,
                    'X-Requested-With': 'XMLHttpRequest'  // ✅ Header adicional para Django
                },
                body: JSON.stringify(data),
                credentials: 'same-origin'  // ✅ Incluir cookies
            });
            
            console.log('📡 Respuesta HTTP:', response.status, response.statusText);
            
            if (!response.ok) {
                console.error('❌ Error HTTP:', response.status);
                
                // Intentar leer el cuerpo del error
                try {
                    const errorText = await response.text();
                    console.error('📄 Cuerpo del error:', errorText.substring(0, 200));
                } catch (e) {
                    console.error('No se pudo leer el cuerpo del error');
                }
                
                return { continuar: true };
            }
            
            const result = await response.json();
            console.log('📥 Respuesta recibida:', result);
            
            if (result.status === 'warning' && result.tiene_conflictos) {
                console.log('🚨 ¡CONFLICTO DETECTADO!');
                mostrarModalConflictos(result, form);
                return { continuar: false };
            } else {
                console.log('✅ No hay conflictos');
                return { continuar: true };
            }
            
        } catch (error) {
            console.error('❌ Error en verificación:', error);
            console.error('Stack:', error.stack);
            return { continuar: true };
        }
    }

    // Inicializar cuando el DOM esté listo
    function inicializar() {
        console.log('🎬 Inicializando verificación de conflictos...');
        
        const form = document.getElementById('solicitudForm');
        
        if (!form) {
            console.error('❌ No se encontró el formulario solicitudForm');
            return;
        }
        
        console.log('✅ Formulario encontrado');
        
        // Marcar que la verificación está activa
        form.dataset.verificacionActiva = 'true';
        
        // Agregar listener al formulario
        form.addEventListener('submit', async (e) => {
            console.log('🔔 Submit event detectado');
            
            // Solo interceptar si la verificación está activa
            if (form.dataset.verificacionActiva !== 'true') {
                console.log('⏩ Verificación desactivada, permitiendo envío');
                return;
            }
            
            e.preventDefault();
            e.stopPropagation();
            
            console.log('🛑 Envío detenido para verificación');
            
            // Verificar conflictos
            const resultado = await verificarConflictos(form);
            
            if (resultado.continuar) {
                console.log('✅ Continuando con envío normal');
                enviarFormularioDirectamente(form);
            } else {
                console.log('⏸️ Envío detenido por conflictos');
            }
        }, true);
        
        console.log('✅ Listener agregado correctamente');
    }

    // Ejecutar cuando el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', inicializar);
    } else {
        inicializar();
    }
    
    console.log('✅ Módulo de verificación de conflictos cargado');
})();