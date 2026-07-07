"""
Django settings for gestion_espacios_academicos project.
"""
import os
from pathlib import Path
from django.contrib.messages import constants as messages

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ============================================
# 🚨 CONFIGURACIÓN DE SEGURIDAD CRÍTICA
# ============================================

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-e*yhj@x@hci!2c#-@i0n3#ej3$=(&vvbqtse5u(b6&naao1rqe')

# SECURITY WARNING: don't run with debug turned on in production!
# 🔧 FIX: Mejorar la lectura de DEBUG
DEBUG = os.environ.get('DEBUG', 'False').lower() in ['true', '1', 'yes']

# 🔧 ALTERNATIVA SIMPLE PARA DESARROLLO:
# Descomenta la siguiente línea para forzar DEBUG en desarrollo
# DEBUG = True

# ⚠️ EN PRODUCCIÓN: cambiar esto por tu dominio real
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

# ============================================
# 🔒 CONFIGURACIÓN DE SESIONES - CRÍTICA
# ============================================
# Reemplaza TODA la sección de sesiones en tu settings.py

# 1️⃣ Motor de sesiones - BASE DE DATOS (nunca cache)
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# 2️⃣ Nombre ÚNICO de cookie
import uuid
SESSION_COOKIE_NAME = f'sessionid_uabjb_{uuid.uuid4().hex[:8]}'  # ✅ Único por instalación

# 3️⃣ Configuración de duración
SESSION_COOKIE_AGE = 43200  # 12 horas
SESSION_SAVE_EVERY_REQUEST = True  # ✅ Actualizar SIEMPRE
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# 4️⃣ Configuración de la cookie
SESSION_COOKIE_PATH = '/'
SESSION_COOKIE_DOMAIN = None  # ✅ CRÍTICO: None = solo dominio actual
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SECURE = False  # False en desarrollo
SESSION_COOKIE_HTTPONLY = True

# 5️⃣ Serialización segura
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'

# 6️⃣ CSRF - También debe ser único
CSRF_COOKIE_NAME = f'csrftoken_uabjb_{uuid.uuid4().hex[:8]}'
CSRF_COOKIE_SECURE = False  # False en desarrollo
CSRF_COOKIE_HTTPONLY = False  # False para CSRF
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_USE_SESSIONS = False  # ✅ False = usar cookie separada

# 7️⃣ Cache - NO cachear sesiones ni vistas autenticadas
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',  # ✅ Sin cache en desarrollo
    }
}

# 8️⃣ Headers de seguridad
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# 9️⃣ En desarrollo, NO usar SSL
if DEBUG:
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

# ============================================
# APPLICATION DEFINITION
# ============================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'gestion_espacios_academicos',
    'administrador',
    'encargados',
    'reportes',
    'usuarios',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'gestion_espacios_academicos.middleware.TimezoneMiddleware',
]

ROOT_URLCONF = 'gestion_espacios_academicos.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'gestion_espacios_academicos.wsgi.application'

# ============================================
# AUTHENTICATION
# ============================================

AUTH_USER_MODEL = 'gestion_espacios_academicos.CustomUser'
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend', 
]

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/usuarios/mi-perfil/'
LOGOUT_REDIRECT_URL = '/'

# ============================================
# EMAIL CONFIGURATION
# ============================================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'cibanezsanguino@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'ofwd qhdu hndd iqbh')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# ============================================
# DATABASE
# ============================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'gestion_espacios_db'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'espacios123'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'CONN_MAX_AGE': 60,
    }
}

# ============================================
# PASSWORD VALIDATION
# ============================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ============================================
# INTERNATIONALIZATION & TIMEZONE
# ============================================

LANGUAGE_CODE = 'es-bo'

USE_I18N = True
USE_L10N = True
USE_TZ = True
TIME_ZONE = 'America/La_Paz'

# Formato de fecha y hora
DATETIME_FORMAT = 'd/m/Y H:i'
DATE_FORMAT = 'd/m/Y'
TIME_FORMAT = 'H:i'

DATETIME_INPUT_FORMATS = [
    '%Y-%m-%d %H:%M:%S',
    '%Y-%m-%d %H:%M',
    '%d/%m/%Y %H:%M:%S',
    '%d/%m/%Y %H:%M',
]

# ============================================
# STATIC & MEDIA FILES
# ============================================

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================
# MESSAGES
# ============================================

MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'error',
}

# ============================================
# 📋 LOGGING (para debugging de sesiones)
# ============================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['console', 'file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# Crear directorio de logs si no existe
os.makedirs(os.path.join(BASE_DIR, 'logs'), exist_ok=True)

# ============================================
# 🔍 DEBUG INFO (útil para desarrollo)
# ============================================
if DEBUG:
    print(f"🔧 DEBUG MODE: {DEBUG}")
    print(f"🔒 SSL REDIRECT: {os.environ.get('SECURE_SSL_REDIRECT', 'Not set')}")
    print(f"🍪 SECURE COOKIES: {SESSION_COOKIE_SECURE}")

# ============================================
# 🔒 CONFIGURACIÓN DE SESIONES - FIX PARA EVITAR MEZCLA
# ============================================
# Agregar/reemplazar esta sección en tu settings.py

# 1️⃣ Motor de sesiones - SIEMPRE base de datos
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# 2️⃣ Nombre ÚNICO de cookie (CRÍTICO)
SESSION_COOKIE_NAME = 'sessionid_uabjb_unique'  # ✅ Debe ser único

# 3️⃣ Configuración de la cookie de sesión
SESSION_COOKIE_AGE = 43200  # 12 horas
SESSION_SAVE_EVERY_REQUEST = True  # ✅ Actualizar en cada request
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# 4️⃣ Path y Domain de la cookie (IMPORTANTE)
SESSION_COOKIE_PATH = '/'  # ✅ Ruta de la cookie
SESSION_COOKIE_DOMAIN = None  # ✅ None = solo el dominio actual
SESSION_COOKIE_SAMESITE = 'Lax'  # ✅ Protección CSRF

# 5️⃣ Seguridad de cookies
SESSION_COOKIE_SECURE = False  # False en desarrollo (HTTP)
SESSION_COOKIE_HTTPONLY = True  # ✅ No accesible desde JavaScript

# 6️⃣ CSRF Protection (también importante)
CSRF_COOKIE_NAME = 'csrftoken_uabjb_unique'  # ✅ Nombre único
CSRF_COOKIE_SECURE = False  # False en desarrollo
CSRF_COOKIE_HTTPONLY = False  # Debe ser False para CSRF
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_USE_SESSIONS = False  # ✅ Mantener en False

# 7️⃣ Cache - NO cachear vistas autenticadas
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'uabjb-unique-cache',
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        }
    }
}

# 8️⃣ MIDDLEWARE - Verificar el orden (CRÍTICO)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',  # ✅ Antes de Auth
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # ✅ Después de Session
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'gestion_espacios_academicos.middleware.SessionDebugMiddleware', 
    'gestion_espacios_academicos.middleware.TimezoneMiddleware',
]

# 9️⃣ Desactivar cache de autenticación
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# 🔟 NO cachear vistas con @login_required
# Esto va en tus decoradores de vista (lo veremos después)