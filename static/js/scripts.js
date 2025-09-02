// ============================
// SISTEMA DE GESTIÓN UABJB
// JavaScript Unificado Completo
// ============================

document.addEventListener('DOMContentLoaded', function () {
    const currentPage = detectCurrentPage();

    switch (currentPage) {
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
            initAuth();
            break;
    }

    initGlobalFeatures();
});

// ============================
// DETECCIÓN DE PÁGINA ACTUAL
// ============================
function detectCurrentPage() {
    const body = document.body;

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
    setupFormNavigation();
    setupLoginForm();
    setupRegisterForm();
    setupInputEffects();
    setupValidations();
    setupRememberMe();
    detectInitialPage();
}

// ============================
// NAVEGACIÓN ENTRE FORMULARIOS
// ============================
function setupFormNavigation() {
    const showRegisterBtn = document.getElementById('showRegisterBtn');
    const showLoginBtn = document.getElementById('showLoginBtn');
    const loginContainer = document.getElementById('loginContainer');
    const registerContainer = document.getElementById('registerContainer');

    if (showRegisterBtn) {
        showRegisterBtn.addEventListener('click', function (e) {
            e.preventDefault();
            console.log('Mostrando formulario de registro');
            if (loginContainer) loginContainer.style.display = 'none';
            if (registerContainer) registerContainer.style.display = 'block';
            document.body.className = 'register-body';
            document.title = 'Registro - UABJB';
        });
    }

    if (showLoginBtn) {
        showLoginBtn.addEventListener('click', function (e) {
            e.preventDefault();
            console.log('Mostrando formulario de login');
            if (registerContainer) registerContainer.style.display = 'none';
            if (loginContainer) loginContainer.style.display = 'block';
            document.body.className = 'login-body';
            document.title = 'Login - Sistema de Gestión UABJB';
        });
    }
}

// ============================
// DETECCIÓN DE PÁGINA INICIAL
// ============================
function detectInitialPage() {
    const urlParams = new URLSearchParams(window.location.search);
    const page = urlParams.get('page');

    if (page === 'register') {
        const btn = document.getElementById('showRegisterBtn');
        if (btn) btn.click();
    }

    if (window.location.pathname.includes('registro')) {
        const btn = document.getElementById('showRegisterBtn');
        if (btn) btn.click();
    }
}

// ============================
// INICIALIZACIÓN DEL LOGIN
// ============================
function initLogin() {
    console.log('Inicializando Login...');
    if (typeof M !== 'undefined') M.AutoInit();
    setupLoginForm();
    setupInputEffects();
    setupRememberMe();
    setupRegisterLink();
}


// ============================
// RECORDAR USUARIO
// ============================
function setupRememberMe() {
    const rememberCheckbox = document.getElementById('remember');
    const usernameInput = document.getElementById('username');
    if (!rememberCheckbox || !usernameInput) return;

    const savedUsername = localStorage.getItem('rememberedUsername');
    if (savedUsername) {
        usernameInput.value = savedUsername;
        rememberCheckbox.checked = true;
    }

    rememberCheckbox.addEventListener('change', function () {
        if (this.checked) {
            if (usernameInput.value) {
                localStorage.setItem('rememberedUsername', usernameInput.value);
            }
        } else {
            localStorage.removeItem('rememberedUsername');
        }
    });

    usernameInput.addEventListener('input', function () {
        if (rememberCheckbox.checked && this.value) {
            localStorage.setItem('rememberedUsername', this.value);
        }
    });
}

// ============================
// ENLACE DE REGISTRO
// ============================
function setupRegisterLink() {
    const link = document.getElementById('showRegister');
    if (link) {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            console.log('Showing register form...');
        });
    }
}

document.addEventListener('DOMContentLoaded', function () {
    const facultadSelect = document.getElementById('id_facultad');
    if (facultadSelect) {
        facultadSelect.addEventListener('change', function () {
            // Marca que el cambio fue interno para no perder datos
            const form = document.getElementById('registerForm');
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = '_facultad_changed';
            input.value = '1';
            form.appendChild(input);
            form.submit();
        });
    }
});

// ============================
// INICIALIZACIÓN DEL DASHBOARD
// ============================
function initDashboard() {
    console.log('Inicializando Dashboard...');
    loadTheme();
    setupThemeToggle();
    setupNavigation();
    setupRippleEffects();
    setTimeout(animateNumbers, 500);
    setupScrollAnimations();
}

// ============================
// TEMA OSCURO / CLARO
// ============================
function toggleTheme() {
    const body = document.body;
    const themeIcon = document.getElementById('themeIcon');
    const themeText = document.getElementById('themeText');

    if (body.getAttribute('data-theme') === 'dark') {
        body.removeAttribute('data-theme');
        if (themeIcon) themeIcon.textContent = '🌙';
        if (themeText) themeText.textContent = 'Modo Oscuro';
        localStorage.setItem('theme', 'light');
    } else {
        body.setAttribute('data-theme', 'dark');
        if (themeIcon) themeIcon.textContent = '☀️';
        if (themeText) themeText.textContent = 'Modo Claro';
        localStorage.setItem('theme', 'dark');
    }
}

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

function setupThemeToggle() {
    const toggle = document.querySelector('.theme-toggle');
    if (toggle) toggle.addEventListener('click', toggleTheme);
}

// ============================
// NAVEGACIÓN ACTIVA
// ============================
function setupNavigation() {
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', function () {
            document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
            this.classList.add('active');
        });
    });
}

// ============================
// EFECTO RIPPLE
// ============================
function setupRippleEffects() {
    document.querySelectorAll('.btn-ripple').forEach(button => {
        button.addEventListener('click', function (e) {
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

// ============================
// ANIMACIÓN DE NÚMEROS
// ============================
function animateNumbers() {
    document.querySelectorAll('.stat-number').forEach(number => {
        const target = parseInt(number.textContent.replace(/,/g, ''));
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

// ============================
// ANIMACIONES AL SCROLL
// ============================
function setupScrollAnimations() {
    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

    document.querySelectorAll('.fade-in').forEach(el => observer.observe(el));
}

// ============================
// EFECTOS DE INPUT
// ============================
function setupInputEffects() {
    document.querySelectorAll('input').forEach(input => {
        input.addEventListener('focus', () => input.parentElement.classList.add('focused'));
        input.addEventListener('blur', () => {
            if (input.value === '') input.parentElement.classList.remove('focused');
        });
    });
}

// ============================
// FUNCIONES GLOBALES
// ============================
function initGlobalFeatures() {
    setupGlobalInputEffects();
}

function setupGlobalInputEffects() {
    document.querySelectorAll('input, select, textarea').forEach(input => {
        input.addEventListener('focus', function () {
            const parent = this.closest('.input-field');
            if (parent) parent.classList.add('focused');
        });
        input.addEventListener('blur', function () {
            const parent = this.closest('.input-field');
            if (parent && this.value === '') parent.classList.remove('focused');
        });
    });
}

// ============================
// UTILIDADES
// ============================
function showToast(message, type = 'info', duration = 4000) {
    if (typeof M !== 'undefined') {
        const classes = { success: 'green darken-2', error: 'red darken-2', warning: 'orange darken-2', info: 'blue darken-2' };
        const icons = { success: 'check_circle', error: 'error', warning: 'warning', info: 'info' };
        M.toast({ html: `<i class="material-icons left">${icons[type] || 'info'}</i>${message}`, classes: classes[type] || 'blue darken-2', displayLength: duration });
    } else {
        console.log(`${type.toUpperCase()}: ${message}`);
    }
}

// Exportar funciones globales
window.UABJB = {
    showToast,
    validateForm: () => true,
    clearForm: () => {},
    formatNumber: (n) => n.toLocaleString(),
    animateOnScroll: () => {},
    debounce: (fn, delay) => setTimeout(fn, delay),
    isMobile: () => window.innerWidth <= 768,
    toggleTheme,
    makeRequest: () => Promise.resolve()
};

// Agregar este script en tu template registro.html
document.addEventListener('DOMContentLoaded', function() {
    const facultadSelect = document.getElementById('id_facultad');
    const carreraSelect = document.getElementById('id_carrera');
    
    facultadSelect.addEventListener('change', function() {
        const facultadId = this.value;
        
        // Limpiar opciones de carrera
        carreraSelect.innerHTML = '<option value="">Seleccionar Carrera</option>';
        
        if (facultadId) {
            // Hacer petición AJAX para obtener carreras
            fetch(`/get_carreras/${facultadId}/`)
                .then(response => response.json())
                .then(data => {
                    data.carreras.forEach(carrera => {
                        const option = document.createElement('option');
                        option.value = carrera.id;
                        option.textContent = carrera.nombre;
                        carreraSelect.appendChild(option);
                    });
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        }
    });
});