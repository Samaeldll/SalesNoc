"""
Django settings for noccode project.

Generated by 'django-admin startproject' using Django 3.2.8.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path, os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = os.path.join(BASE_DIR, 'front')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-z3i^c^%$o57pqiv(*pypy%fb8xg2bi#$g@++y!l_q_ybbe4j))'

# SECURITY WARNING: don't run with debug turned on in production!

DEBUG = True

ALLOWED_HOSTS = []
if DEBUG:
    ALLOWED_HOSTS.append("127.0.0.1")

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 'debug_toolbar',
    "crispy_forms",
    "crispy_bootstrap5",
    'widget_tweaks',
    'front',
    'django.contrib.postgres',
    'django_telegram_login',
    #'webpush',
]


TELEGRAM_BOT_NAME = 'SalesMessegeBot'
TELEGRAM_BOT_API_KEY = '5719831333:AAGQRckoFetvdilkNXh8nw7rcKC77RQNRf4'

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5" #новое

CRISPY_TEMPLATE_PACK = "bootstrap5" #новое

MIDDLEWARE = [
    #'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
    'front.middleware.timing_check'
]

ROOT_URLCONF = 'noccode.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
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

WSGI_APPLICATION = 'noccode.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
         'ENGINE': 'django.db.backends.postgresql',
         'NAME': 'django_project',
         'USER': 'postgres',
         'PASSWORD':'postgres',
         'HOST':'localhost',
         'PORT': 5432
     }
}

REST_FRAMEWORK = {
    'DATETIME_FORMAT': "%d.%m.%Y %H:%M:%S",
}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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



log_path_to_file_info = 'E:\WorkProject\work\logsME\log_sms_information.log'
log_path_to_file_error = 'E:\WorkProject\work\logsME\log_sms_errors.log'
log_path_to_file_response = 'E:\WorkProject\work\logsME\log_sms_response.log'
log_maxBytes_logger_info = 1024 # 1КБ
log_maxBytes_logger_error = 1024 # 1КБ
log_maxBytes_logger_response = 1024 # 1КБ
log_max_backupfile_Count = 5 #Its for all loggers

os.chmod(log_path_to_file_error, 0o777)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'sms_class_all': {
            'format': '%(asctime)s %(message)s',
            'datefmt': "%Y-%m-%d %H:%M:%S",
        },
    },
    'handlers': {
        'sms_file_information': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': log_path_to_file_info,
            'formatter': 'sms_class_all',
            'maxBytes': log_maxBytes_logger_info,
            'backupCount': log_max_backupfile_Count,
            'encoding': 'UTF-8',
        },
        'sms_file_errors': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': log_path_to_file_error,
            'maxBytes': log_maxBytes_logger_error,
            'backupCount': log_max_backupfile_Count,
            'encoding': 'UTF-8',
            'formatter': 'sms_class_all',
        },
        'sms_file_response': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': log_path_to_file_response,
            'maxBytes': log_maxBytes_logger_response,
            'backupCount': log_max_backupfile_Count,
            'encoding': 'UTF-8',
            'formatter': 'sms_class_all',
        },
    },
    'loggers': {
        'sms_cry_information': {
            'handlers': ['sms_file_information'],
            'level': 'INFO',
            'propagate': True,
            },
        'sms_cry_errors': {
            'handlers': ['sms_file_errors'],
            'level': 'ERROR',
            'propagate': True,
            },
        'sms_cry_response': {
            'handlers': ['sms_file_response'],
            'level': 'DEBUG',
            'propagate': True,
            },
    },
}

AUTH_USER_MODEL = 'front.FrontUser'

INTERNAL_IPS = [
    '127.0.0.1',
]

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'Europe/Kiev'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(FRONTEND_DIR, 'static')

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'