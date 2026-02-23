import os
from pathlib import Path
import environ
import sys

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False)
)
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env('ALLOWED_HOSTS').split(',') if env('ALLOWED_HOSTS') else []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'rest_framework',
    'rest_framework_gis',
    'django_filters',
    'destinations',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'tourism_portal.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'tourism_portal.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': env('DATABASE_NAME', default='tourism_db'),
        'USER': env('DATABASE_USER', default='postgres'),
        'PASSWORD': env('DATABASE_PASSWORD', default='postgres'),
        'HOST': env('DATABASE_HOST', default='localhost'),
        'PORT': env('DATABASE_PORT', default='5432'),
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# During development, also look for static files in the project `static/` folder
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend']
}

# Point to GDAL/GEOS DLLs and PROJ data inside a local 'gisenv' virtualenv if present.
# This mirrors a working Windows setup where GDAL was installed into a project venv.
candidates = []

# project-local 'gisenv' (optional)
candidates.append(os.path.join(str(BASE_DIR), 'gisenv', 'Lib', 'site-packages', 'osgeo'))

# current active venv (sys.prefix)
candidates.append(os.path.join(sys.prefix, 'Lib', 'site-packages', 'osgeo'))

# common site-packages under project venv folder names
candidates.append(os.path.join(str(BASE_DIR), '.venv', 'Lib', 'site-packages', 'osgeo'))
candidates.append(os.path.join(str(BASE_DIR), 'venv', 'Lib', 'site-packages', 'osgeo'))

found = False
for venv_osgeo in candidates:
    if os.path.exists(venv_osgeo):
        gdal_dll = os.path.join(venv_osgeo, 'gdal.dll')
        geos_dll = os.path.join(venv_osgeo, 'geos_c.dll')
        data_dir = os.path.join(venv_osgeo, 'data')
        if os.path.exists(gdal_dll):
            GDAL_LIBRARY_PATH = gdal_dll
            # add containing dir to PATH so loader can find related DLLs
            os.environ['PATH'] = os.path.dirname(gdal_dll) + os.pathsep + os.environ.get('PATH', '')
            found = True
        if os.path.exists(geos_dll):
            GEOS_LIBRARY_PATH = geos_dll
            os.environ['PATH'] = os.path.dirname(geos_dll) + os.pathsep + os.environ.get('PATH', '')
            found = True
        if os.path.exists(data_dir):
            PROJ_LIB = data_dir
            os.environ.setdefault('PROJ_LIB', PROJ_LIB)
            found = True
        if found:
            break

# As a last resort, allow manual override via environment variables or .env
if not found:
    # If user set explicit paths in environment or .env, respect them
    gpath = env('GDAL_LIBRARY_PATH', default=None)
    geopath = env('GEOS_LIBRARY_PATH', default=None)
    projpath = env('PROJ_LIB', default=None)
    if gpath:
        GDAL_LIBRARY_PATH = gpath
    if geopath:
        GEOS_LIBRARY_PATH = geopath
    if projpath:
        os.environ.setdefault('PROJ_LIB', projpath)
