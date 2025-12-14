"""
Django settings for kmeans_project project.
"""

from pathlib import Path
import os  # Necesario para manejar variables de entorno y rutas

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# 1. SEGURIDAD: Usar una variable de entorno para la SECRET_KEY en producción
# Si no encuentra la variable de entorno (ej., en desarrollo local), usa la clave por defecto.
SECRET_KEY = os.environ.get(
    "SECRET_KEY", 
    "django-insecure-!1w=zn1yw4vus#e+0#q%w7!g0%z&^w&qt=@+q6o&szhc8kf7#i"
)

# 2. MODO DE DEBUG
# Se recomienda usar DEBUG=False en producción.
# Render (o Gunicorn) lo manejará con la variable de entorno.
DEBUG = os.environ.get("DEBUG", "True") == "True"

# 3. ALLOWED_HOSTS: Permitir el dominio de Render
# '*' es necesario para el despliegue inicial en Render.
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")
if DEBUG:
    ALLOWED_HOSTS = ["*"]


# Application definition

# 4. INSTALLED_APPS: Añadir WhiteNoise para servir estáticos en producción
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Terceros
    'rest_framework',
    'whitenoise.runserver_nostatic',  # Optimización para desarrollo (opcional)
    # Aplicaciones locales
    'fraud_detection_api',
]

# 5. MIDDLEWARE: Añadir WhiteNoise para servir estáticos
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # Nuevo: Middleware de WhiteNoise para servir archivos estáticos de forma eficiente
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "kmeans_project.urls"

# 6. TEMPLATES: Consolidación (Eliminé el bloque duplicado)
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "kmeans_project.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",},
]


# Internationalization
# https://docs.docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# 7. STATIC FILES: Configuración para WhiteNoise y Render
STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # Directorio donde se recolectan los estáticos

# 8. MÁXIMO TAMAÑO DE ARCHIVO (ya estaba en tu código, se mantiene)
FILE_UPLOAD_MAX_MEMORY_SIZE = 104857600
DATA_UPLOAD_MAX_MEMORY_SIZE = 104857600 # 100 MB


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# 9. CONFIGURACIÓN ADICIONAL PARA WHITENOISE
# Comprimir los archivos estáticos
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

FORCE_SCRIPT_NAME = "/"