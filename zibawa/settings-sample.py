"""
Django settings for zibawa project.

For the full list of settings and their values, see
https://docs.zibawa.com/
"""

import os
import logging

#logger = logging.getLogger('django_auth_ldap')
#logger.addHandler(logging.StreamHandler())
#logger.setLevel(logging.DEBUG)


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
	    'level':'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file': {
            'level': 'ERROR',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': '/var/log/zibawa/zibawa.log',
            'formatter': 'verbose',
            'when': 'midnight',
            'backupCount': 5,
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console','file'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
        },
       'devices': {
           'handlers': ['console','file'],
           'level': 'DEBUG'
        },
       'stack_configs': {
            'handlers': ['console','file'],
            'level': 'DEBUG'
        },   
       'django_auth_ldap': {
            'handlers': ['console','file'],
            'level': 'DEBUG'
        },
        'front': {
            'handlers': ['console','file'],
            'level': 'DEBUG'
        },
	'simulator': {
            'handlers': ['console','file'],
            'level': 'DEBUG'
        },
    },
}


#Update with the paths to your LDAP certificates
#make sure hostname matches that on your certificate is using tls


LDAP3={'host':'ldap.zibawa.com',
       'port':389,
       'use_start_tls': True,
       'path_to_ca_cert':'/etc/ssl/certs/ca_server.pem',
       'validate_certs':True,
       'path_to_client_cert':'/etc',
       'path_to_key':'/etc' ,
       }

#maps LDAP attributes to Zibawa User attributes 
LDAP3_ATTR_MAP = {
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail"
    
}


LDAP3_USER_FLAGS_BY_GROUP = {
    "is_active": "active",
    "is_staff": "editor",
    "is_superuser": "superuser"
}

# Baseline configuration.
#'/home/julimatt/jmmserver/ca_server.pem'
#AUTH_LDAP_SERVER_URI = str("ldap://ldap.myserver.com")
#this is the DN of the LDAP super user
AUTH_LDAP_BIND_DN = str("cn=admin,dc=zibawa,dc=com")
AUTH_LDAP_BIND_PASSWORD = str("secretpassword")
AUTH_LDAP_USERS_OU_DN="ou=users,dc=zibawa,dc=com"
AUTH_LDAP_GROUPS_OU_DN="ou=groups,dc=zibawa,dc=com"



AUTHENTICATION_BACKENDS = (
    'front.backends.OpenLdapBackend',
    
    )



# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'e2klwicpo&*+2k1neyz6j-3-#a&k&5jq$$x0p*fa70qgkigufh'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost','127.0.0.1','.zibawa.com']
SITE_URL="app.zibawa.com"

# Application definition

INSTALLED_APPS = [
   
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'devices.apps.DevicesConfig',
    'hooks.apps.HooksConfig',
    'stack_configs.apps.StackConfigsConfig',
    'simulator.apps.SimulatorConfig',
    'front.apps.FrontConfig',
    
]

LOGIN_URL='/front/login/'
LOGIN_REDIRECT_URL = '/admin/'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'zibawa.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,'templates')],
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

WSGI_APPLICATION = 'zibawa.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'zibawadb',
        'USER': 'zibawauser',
        'PASSWORD': 'mysecretpassword',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/
STATIC_ROOT= '/var/www/html/zibawa/static/'
STATIC_URL = '/static/'



#add grafana data here
DASHBOARD={'host':'dashboard.zibawa.com','port':'443',
           'user':'admin','password':'mysecretpassword',
           'use_ssl': True, 
           'path_to_ca_cert':'/home/zibawa/DSTRootCAX3certificate.pem',
           'verify_certs':True,
	   'path_to_client_cert':None,
           'path_to_key':None}

#CHOOSE EITHER INFLUXDB OR ELASTICSEARCH (CANNOT USE BOTH)  

DATASTORE=('INFLUXDB')

ELASTICSEARCH={'host':'http://192.168.1.10','port':'9200',
           'user':'elasticsearch','password':'mysecretpassword',
           'use_ssl': False,'path_to_ca_cert':'/etc',
           'path_to_client_cert':'/etc',
           'path_to_key':'/etc' }

INFLUXDB={'host':'zibawa.com','port':8086,
           'user':'influx',
           'password':'mysecretpassword',
           'use_ssl': True,'path_to_ca_cert':'/home/zibawa/DSTRootCAX3certificate.pem',
	   'verify_certs':True,
           'path_to_client_cert':None,
           'path_to_key':None }

#do not include http:// for host!
#if not using certificates, set to None (without ")
#
RABBITMQ={'host':'zibawa.com','port':5671,
           'user':'zadmin',
           'password':'mysecretpassword',
           'use_ssl': True,   #True or False without "
           'verify_certs':True,
	   'path_to_ca_cert':'/home/zibawa/DSTRootCAX3certificate.pem',
           'path_to_client_cert':None,#set to None (without ") if no certs
           'path_to_key':None }

#used for testing. Settings should be as setup in rabbitMQ.config MQTT settings 
#currently there is no "superuser for MQTT, so user and password are not set

MQTT={'host':'zibawa.com','port':8883,
           'use_ssl': True,#True or False without "
           'verify_certs':True,
           'path_to_ca_cert':'/home/zibawa/DSTRootCAX3certificate.pem',# !CARE! this certificate is published and downloadable to users
           }


EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'me@gmail.com'
EMAIL_HOST_PASSWORD = 'myemailpassword'
EMAIL_USE_TLS = True
