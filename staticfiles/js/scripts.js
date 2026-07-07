// ============================
// SISTEMA DE GESTIÓN UABJB
// JavaScript Unificado Completo
// ============================

document.addEventListener('DOMContentLoaded', function() {
    // Detectar qué página estamos cargando
    const currentPage = detectCurrentPage();
    
    // Inicializar según la página
    switch(currentPage) {
        case 'dashboard':
            initDashboard();
            break;
        case 'login':
            initLogin();
            break;
        case 'register':
            initRegister();
            break;
        case 'auth':
            initAuth(); // Para el HTML unificado
            break;
    }
    
    // Funciones globales
    initGlobalFeatures();
});

// ============================
// DETECCIÓN DE PÁGINA ACTUAL
// ============================
function detectCurrentPage() {
    const body = document.body;
    
    // Detectar HTML unificado de autenticación
    if (body.classList.contains('auth-body') || 
        (document.querySelector('#loginContainer') && document.querySelector('#registerContainer'))) {
        return 'auth';
    }
    
    if (body.classList.contains('dashboard-body') || document.querySelector('.dashboard')) {
        return 'dashboard';
    } else if (body.classList.contains('login-body') || document.querySelector('.login-card')) {
        return 'login';
    } else if (body.classList.contains('register-body') || document.querySelector('.register-card')) {
        return 'register';
    }
    
    // Fallback: detectar por elementos específicos
    if (document.querySelector('.welcome-card')) return 'dashboard';
    if (document.querySelector('#loginForm')) return 'login';
    if (document.querySelector('#registerForm')) return 'register';
    
    return 'unknown';
}

// ============================
// INICIALIZACIÓN DEL HTML UNIFICADO
// ============================
function initAuth() {
    console.log('Inicializando sistema de autenticación unificado...');
    
    // Configurar navegación entre formularios
    setupFormNavigation();
    
    // Configurar formulario de login
    setupLoginForm();
    
    // Configurar formulario de registro
    setupRegisterForm();
    
    // Configurar efectos de input
    setupInputEffects();
    
    // Configurar validaciones
    setupValidations();
    
    // Configurar función "recordar usuario"
    setupRememberMe();
    
    // Detectar página inicial según URL o parámetros
    detectInitialPage();
}

// ============================
// NAVEGACIÓN ENTRE FORMULARIOS (NUEVO)
// ============================
function setupFormNavigation() {
    const showRegisterBtn = document.getElementById('showRegisterBtn');
    const showLoginBtn = document.getElementById('showLoginBtn');
    const loginContainer = document.getElementById('loginContainer');
    const registerContainer = document.getElementById('registerContainer');
    
    // Mostrar registro
    if (showRegisterBtn) {
        showRegisterBtn.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Mostrando formulario de registro');
            
            if (loginContainer) loginContainer.style.display = 'none';
            if (registerContainer) registerContainer.style.display = 'block';
            
            // Cambiar clase del body para estilos específicos
            document.body.className = 'register-body';
            
            // Cambiar título de la página
            document.title = 'Registro - UABJB';
        });
    }
    
    // Mostrar login
    if (showLoginBtn) {
        showLoginBtn.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Mostrando formulario de login');
            
            if (registerContainer) registerContainer.style.display = 'none';
            if (loginContainer) loginContainer.style.display = 'block';
            
            // Cambiar clase del body para estilos específicos
            document.body.className = 'login-body';
            
            // Cambiar título de la página
            document.title = 'Login - Sistema de Gestión UABJB';
        });
    }
}

// ============================
// DETECCIÓN DE PÁGINA INICIAL (NUEVO)
// ============================
function detectInitialPage() {
    const urlParams = new URLSearchParams(window.location.search);
    const page = urlParams.get('page');
    
    // Si hay parámetro page=register, mostrar registro
    if (page === 'register') {
        const showRegisterBtn = document.getElementById('showRegisterBtn');
        if (showRegisterBtn) {
            showRegisterBtn.click();
        }
    }
    
    // Si la URL contiene 'registro', mostrar registro
    if (window.location.pathname.includes('registro')) {
        const showRegisterBtn = document.getElementById('showRegisterBtn');
        if (showRegisterBtn) {
            showRegisterBtn.click();
        }
    }
}

// ============================
// INICIALIZACIÓN DEL DASHBOARD
// ============================
function initDashboard() {
    console.log('Inicializando Dashboard...');
    
    // Cargar tema guardado
    loadTheme();
    
    // Configurar toggle de tema
    setupThemeToggle();
    
    // Configurar navegación activa
    setupNavigation();
    
    // Configurar efectos ripple
    setupRippleEffects();
    
    // Iniciar animación de números
    setTimeout(animateNumbers, 500);
    
    // Configurar observer para animaciones
    setupScrollAnimations();
}

// Toggle entre modo claro y oscuro
function toggleTheme() {
    const body = document.body;
    const themeIcon = document.getElementById('themeIcon');
    const themeText = document.getElementById('themeText');
    
    if (body.getAttribute('data-theme') === 'dark') {
        body.removeAttribute('data-theme');
        themeIcon.textContent = '🌙';
        themeText.textContent = 'Modo Oscuro';
        localStorage.setItem('theme', 'light');
    } else {
        body.setAttribute('data-theme', 'dark');
        themeIcon.textContent = '☀️';
        themeText.textContent = 'Modo Claro';
        localStorage.setItem('theme', 'dark');
    }
}

// Cargar tema guardado
function loadTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    const themeIcon = document.getElementById('themeIcon');
    const themeText = document.getElementById('themeText');
    
    if (savedTheme === 'dark') {
        document.body.setAttribute('data-theme', 'dark');
        if (themeIcon) themeIcon.textContent = '☀️';
        if (themeText) themeText.textContent = 'Modo Claro';
    }
}

// Configurar toggle de tema
function setupThemeToggle() {
    const themeToggle = document.querySelector('.theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
}

// Navegación activa
function setupNavigation() {
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', function() {
            document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
            this.classList.add('active');
        });
    });
}

// Efecto ripple en botones
function setupRippleEffects() {
    document.querySelectorAll('.btn-ripple').forEach(button => {
        button.addEventListener('click', function(e) {
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            const ripple = document.createElement('span');
            ripple.classList.add('ripple');
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            
            this.appendChild(ripple);
            
            setTimeout(() => ripple.remove(), 600);
        });
    });
}

// Animación de números contador
function animateNumbers() {
    const numbers = document.querySelectorAll('.stat-number');
    numbers.forEach(number => {
        const target = parseInt(number.textContent.replace(',', ''));
        const increment = target / 50;
        let current = 0;
        
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            number.textContent = Math.floor(current).toLocaleString();
        }, 30);
    });
}

// Detección de scroll para animaciones
function setupScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    // Observar elementos fade-in
    document.querySelectorAll('.fade-in').forEach(el => {
        observer.observe(el);
    });
}

// ============================
// INICIALIZACIÓN DEL LOGIN
// ============================
function initLogin() {
    console.log('Inicializando Login...');
    
    // Inicializar Materialize si está disponible
    if (typeof M !== 'undefined') {
        M.AutoInit();
    }
    
    // Configurar formulario de login
    setupLoginForm();
    
    // Configurar efectos de input
    setupInputEffects();
    
    // Configurar recordar usuario
    setupRememberMe();
    
    // Configurar enlace de registro
    setupRegisterLink();
}

function setupLoginForm() {
    const loginForm = document.getElementById('loginForm');
    if (!loginForm) return;
    
    const loadingSpinner = document.querySelector('.loading');
    const btnText = document.querySelector('.btn-text');
    
    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        
        if (!username || !password) {
            showToast('Por favor completa todos los campos', 'error');
            return;
        }
        
        // Mostrar loading
        if (loadingSpinner) loadingSpinner.style.display = 'inline-block';
        if (btnText) btnText.textContent = 'Iniciando sesión...';
        
        // Simular petición de login (reemplazar con tu lógica)
        setTimeout(() => {
            console.log('Login attempt:', { username, password });
            
            showToast('¡Bienvenido al sistema!', 'success');
            
            // Redirigir al dashboard
            setTimeout(() => {
                console.log('Redirecting to dashboard...');
                // window.location.href = 'dashboard.html';
            }, 1500);
            
            // Ocultar loading
            if (loadingSpinner) loadingSpinner.style.display = 'none';
            if (btnText) btnText.textContent = 'Iniciar Sesión';
            
        }, 2000);
    });
}

function setupRememberMe() {
    const rememberCheckbox = document.getElementById('remember');
    const usernameInput = document.getElementById('username');
    
    if (!rememberCheckbox || !usernameInput) {
        console.log('Checkbox o input de usuario no encontrado');
        return;
    }
    
    // Cargar usuario guardado
    const savedUsername = localStorage.getItem('rememberedUsername');
    
    if (savedUsername) {
        usernameInput.value = savedUsername;
        rememberCheckbox.checked = true;
    }
    
    // Manejar cambios en el checkbox
    rememberCheckbox.addEventListener('change', function() {
        console.log('Checkbox recordarme cambiado:', this.checked);
        
        if (this.checked) {
            const username = usernameInput.value;
            if (username) {
                localStorage.setItem('rememberedUsername', username);
                showToast('Usuario será recordado', 'info');
            }
        } else {
            localStorage.removeItem('rememberedUsername');
            showToast('Usuario no será recordado', 'info');
        }
    });
    
    // También guardar cuando se escriba en el input si el checkbox está marcado
    usernameInput.addEventListener('input', function() {
        if (rememberCheckbox.checked && this.value) {
            localStorage.setItem('rememberedUsername', this.value);
        }
    });
}

function setupRegisterLink() {
    const registerLink = document.getElementById('showRegister');
    if (!registerLink) return;
    
    registerLink.addEventListener('click', function(e) {
        e.preventDefault();
        console.log('Showing register form...');
        showToast('Redirigiendo a registro...', 'info');
        // window.location.href = 'register.html';
    });
}

// ============================
// INICIALIZACIÓN DEL REGISTRO
// ============================
function initRegister() {
    console.log('Inicializando Registro...');
    
    // Inicializar Materialize si está disponible
    if (typeof M !== 'undefined') {
        M.AutoInit();
        
        // Inicializar selects
        const elems = document.querySelectorAll('select');
        M.FormSelect.init(elems);
    }
    
    // Configurar validación de contraseña
    setupPasswordValidation();
    
    // Configurar formulario de registro
    setupRegisterForm();
    
    // Configurar validación de email
    setupEmailValidation();
    
    // Configurar enlace de login
    setupLoginLink();
}

function setupPasswordValidation() {
    const passwordInput = document.getElementById('password') || document.getElementById('regPassword');
    const confirmPasswordInput = document.getElementById('confirmPassword');
    
    if (passwordInput) {
        passwordInput.addEventListener('input', function() {
            validatePasswordStrength(this.value);
        });
    }
    
    if (confirmPasswordInput) {
        confirmPasswordInput.addEventListener('input', function() {
            const password = passwordInput ? passwordInput.value : '';
            const confirmPassword = this.value;
            
            if (confirmPassword && password !== confirmPassword) {
                this.setCustomValidity('Las contraseñas no coinciden');
            } else {
                this.setCustomValidity('');
            }
        });
    }
}

function validatePasswordStrength(password) {
    const strengthElement = document.getElementById('passwordStrength');
    if (!strengthElement) return;
    
    const strengthBar = strengthElement.querySelector('.strength-bar');
    const strengthText = strengthElement.querySelector('.strength-text');
    
    if (password.length === 0) {
        strengthElement.style.display = 'none';
        return;
    }
    
    strengthElement.style.display = 'block';
    
    let strength = 0;
    let feedback = '';
    
    // Criterios de fortaleza
    if (password.length >= 8) strength++;
    if (/[a-z]/.test(password)) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/[0-9]/.test(password)) strength++;
    if (/[^A-Za-z0-9]/.test(password)) strength++;
    
    // Actualizar visualización
    strengthBar.className = 'strength-bar';
    if (strength <= 2) {
        strengthBar.classList.add('strength-weak');
        feedback = 'Contraseña débil';
    } else if (strength <= 3) {
        strengthBar.classList.add('strength-medium');
        feedback = 'Contraseña media';
    } else {
        strengthBar.classList.add('strength-strong');
        feedback = 'Contraseña fuerte';
    }
    
    if (strengthText) strengthText.textContent = feedback;
}

function setupRegisterForm() {
    const registerForm = document.getElementById('registerForm');
    if (!registerForm) return;
    
    registerForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const button = document.getElementById('registerBtn');
        const loading = document.getElementById('loading');
        
        // Validar contraseñas
        const password = document.getElementById('password') || document.getElementById('regPassword');
        const confirmPassword = document.getElementById('confirmPassword');
        
        if (password && confirmPassword && password.value !== confirmPassword.value) {
            showToast('Las contraseñas no coinciden', 'error');
            return;
        }
        
        // Validar términos
        const termsCheckbox = document.getElementById('terms');
        if (termsCheckbox && !termsCheckbox.checked) {
            showToast('Debes aceptar los términos y condiciones', 'error');
            return;
        }
        
        // Mostrar loading
        if (button) {
            button.disabled = true;
            button.innerHTML = '<div class="loading"></div>Creando cuenta...';
        }
        if (loading) loading.style.display = 'inline-block';
        
        // Simular registro (aquí iría la lógica real)
        setTimeout(() => {
            // Resetear botón
            if (button) {
                button.disabled = false;
                button.innerHTML = 'Crear mi cuenta';
            }
            if (loading) loading.style.display = 'none';
            
            showToast('¡Cuenta creada exitosamente! Verificar tu email.', 'success');
            
            // Si estamos en el HTML unificado, cambiar al login
            const showLoginBtn = document.getElementById('showLoginBtn');
            if (showLoginBtn) {
                setTimeout(() => showLoginBtn.click(), 2000);
            }
            
        }, 2000);
    });
}

function setupEmailValidation() {
    const emailInput = document.getElementById('email');
    if (!emailInput) return;
    
    emailInput.addEventListener('blur', function() {
        const email = this.value;
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        
        if (email && !emailRegex.test(email)) {
            this.setCustomValidity('Por favor ingresa un email válido');
            showToast('Por favor ingresa un email válido', 'error');
        } else {
            this.setCustomValidity('');
        }
    });
}

function setupLoginLink() {
    const loginLinks = document.querySelectorAll('a[onclick="goToLogin()"]');
    loginLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            goToLogin();
        });
    });
}

function goToLogin() {
    console.log('Redirigir al login');
    // window.location.href = 'login.html';
}

// ============================
// CONFIGURACIÓN DE VALIDACIONES (MEJORADO)
// ============================
function setupValidations() {
    // Reutilizar las funciones ya existentes
    setupPasswordValidation();
    setupEmailValidation();
}

// ============================
// FUNCIONES GLOBALES
// ============================
function initGlobalFeatures() {
    // Configurar efectos de animación en los inputs
    setupGlobalInputEffects();
}

function setupInputEffects() {
    const inputs = document.querySelectorAll('input');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        
        input.addEventListener('blur', function() {
            if (this.value === '') {
                this.parentElement.classList.remove('focused');
            }
        });
    });
}

function setupGlobalInputEffects() {
    const inputs = document.querySelectorAll('input, select, textarea');
    
    inputs.forEach(input => {
        // Efecto focus
        input.addEventListener('focus', function() {
            const parent = this.closest('.input-field');
            if (parent) {
                parent.classList.add('focused');
            }
        });
        
        // Efecto blur
        input.addEventListener('blur', function() {
            const parent = this.closest('.input-field');
            if (parent && this.value === '') {
                parent.classList.remove('focused');
            }
        });
        
        // Validación en tiempo real
        input.addEventListener('input', function() {
            this.setCustomValidity('');
        });
    });
}

// ============================
// UTILIDADES
// ============================

// Sistema de notificaciones mejorado
function showToast(message, type = 'info', duration = 4000) {
    // Si Materialize está disponible
    if (typeof M !== 'undefined') {
        const classes = {
            'success': 'green darken-2',
            'error': 'red darken-2',
            'warning': 'orange darken-2',
            'info': 'blue darken-2'
        };
        
        const icons = {
            'success': 'check_circle',
            'error': 'error',
            'warning': 'warning',
            'info': 'info'
        };
        
        M.toast({
            html: `<i class="material-icons left">${icons[type] || 'info'}</i>${message}`,
            classes: classes[type] || 'blue darken-2',
            displayLength: duration
        });
    } else {
        // Fallback para navegadores sin Materialize
        console.log(`${type.toUpperCase()}: ${message}`);
        
        // Crear toast personalizado
        createCustomToast(message, type, duration);
    }
}

function createCustomToast(message, type, duration) {
    // Crear contenedor de toasts si no existe
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
            display: flex;
            flex-direction: column;
            gap: 10px;
        `;
        document.body.appendChild(toastContainer);
    }
    
    // Crear toast
    const toast = document.createElement('div');
    const colors = {
        'success': '#4caf50',
        'error': '#f44336',
        'warning': '#ff9800',
        'info': '#2196f3'
    };
    
    toast.style.cssText = `
        background: ${colors[type] || colors.info};
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        font-size: 14px;
        font-weight: 500;
        max-width: 350px;
        opacity: 0;
        transform: translateX(100%);
        transition: all 0.3s ease;
    `;
    
    toast.textContent = message;
    toastContainer.appendChild(toast);
    
    // Animar entrada
    setTimeout(() => {
        toast.style.opacity = '1';
        toast.style.transform = 'translateX(0)';
    }, 10);
    
    // Animar salida y remover
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }, duration);
}

// Función para validar formularios
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.setCustomValidity('Este campo es obligatorio');
            isValid = false;
        } else {
            field.setCustomValidity('');
        }
    });
    
    return isValid;
}

// Función para limpiar formulario
function clearForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    form.reset();
    
    // Limpiar clases de validación personalizadas
    const inputs = form.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
        input.setCustomValidity('');
        const parent = input.closest('.input-field');
        if (parent) {
            parent.classList.remove('focused', 'error', 'success');
        }
    });
}

// Función para formatear números
function formatNumber(num) {
    return num.toLocaleString();
}

// Función para animar elementos al hacer scroll
function animateOnScroll(selector, animationClass = 'fade-in') {
    const elements = document.querySelectorAll(selector);
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add(animationClass);
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });
    
    elements.forEach(el => observer.observe(el));
}

// Función de debounce para optimizar eventos
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Función para detectar dispositivo móvil
function isMobile() {
    return window.innerWidth <= 768;
}

// Función para hacer peticiones AJAX (opcional)
function makeRequest(url, method = 'GET', data = null) {
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        xhr.open(method, url);
        xhr.setRequestHeader('Content-Type', 'application/json');
        
        xhr.onload = function() {
            if (xhr.status >= 200 && xhr.status < 300) {
                try {
                    const response = JSON.parse(xhr.responseText);
                    resolve(response);
                } catch (e) {
                    resolve(xhr.responseText);
                }
            } else {
                reject(new Error(`Request failed with status ${xhr.status}`));
            }
        };
        
        xhr.onerror = function() {
            reject(new Error('Network error'));
        };
        
        if (data) {
            xhr.send(JSON.stringify(data));
        } else {
            xhr.send();
        }
    });
}

// Exportar funciones globales para uso externo
window.UABJB = {
    showToast,
    validateForm,
    clearForm,
    formatNumber,
    animateOnScroll,
    debounce,
    isMobile,
    makeRequest,
    toggleTheme
};