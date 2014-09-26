"""
Django settings for eCard project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '3nz65lf%m1vb7rz55r2_qrasw9i_#yit$r@&h-764z%7*i3j*p'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = [
    '140.122.185.34',
    '127.0.0.1',
    'localhost',
]


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'web_app',
    'csvimport',

)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = '_eCard.urls'

WSGI_APPLICATION = '_eCard.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'zh-tw'

TIME_ZONE = 'Asia/Taipei'

USE_I18N = True

USE_L10N = True

USE_TZ = True





STATIC_URL = '/static/'
STATIC_ROOT = '/var/www/ecard1.5_static/' # output folder

MEDIA_ROOT = '/var/www/ecard1.5_media/'#server absolute path
MEDIA_URL = '/static/media/'




# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
"""
MEDIA_ROOT = '/var/www/ecard1.5_media/'#server absolute path
# MEDIA_ROOT = 'answers_file/'          for local
MEDIA_URL = 'media/'

STATIC_URL = '/static/'
TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'templates')]
# ----------------------------------------------------------
# Serving static files in production
# http://blog.doismellburning.co.uk/2012/06/25/django-and-static-files/
# ----------------------------------------------------------
# settings
#STATICFILES_DIRS = (os.path.join(BASE_DIR, "path/to/folder/which/not/named/as/static"),) # input folders
STATIC_ROOT = '/var/www/ecard1.5_static/' # output folder
#STATIC_ROOT = 'C:/django_projects/ecard1.5_static/' # output folder
"""
# And the followings need to be added to http.conf:
#
#Alias /static/ "/var/www/ecard1.5_static/" # i.e.: Alias STATIC_URL STATIC_ROOT
#<Directory "/var/www/ecard1.5_static/">
#    Order deny,allow
#    Require all granted
#</Directory>

# Finally, run command: $ python manage.py collectstatic
# All the static files in $app_name/static/ and STATICFILES_DIRS will be collected to STATIC_ROOT
