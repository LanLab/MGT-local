"""
Django settings for Mgt project.

Generated by 'django-admin startproject' using Django 1.11.7.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

DEFAULT_AUTO_FIELD='django.db.models.AutoField'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '' # CHANGE add random string

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['0.0.0.0', 'localhost', '127.0.0.1', '[::1]', '*']

INSTALLED_APPS = [
    # CHANGE add new databases here
    'django_tables2',
    'Home',
    'MGTdb_shared',
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
	'rest_framework',
	'django_registration',
	'django_countries',
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

ROOT_URLCONF = 'Mgt.urls_template'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'Home/templates/'), os.path.join(BASE_DIR, 'Home/templates/')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
				'Mgt.context_processors.root_url',
            ],
        },
    },
]

TEMPLATE_DEBUG = True

TEMPLATE_LOADERS = (
    'django.template.loaders.app_directories.load_template_source',
)

MANAGEMENT_COMMANDS = ['Mgt.management.commands.show_urls']

# MY_URL = "http://mgtdb.unsw.edu.au"
MY_URL = "http://127.0.0.1:8000"
WSGI_APPLICATION = 'Mgt.wsgi.application'

FILE_UPLOAD_PERMISSIONS=0o774
FILE_UPLOAD_DIRECTORY_PERMISSIONS=0o774

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

# 2018, Jan 9 - require a db router (if multiple databases)
NCBI_RETRIEVAL_FREQUENCY = {'Clawclip': None } # CHANGE 

DATABASE_ROUTERS = ['Mgt.router.GenericRouter']
APPS_DATABASE_MAPPING = {'Clawclip': 'blankdb'} # CHANGE key should be in uppercase and value should be in lowercase (i.e. 'Salmonella': 'salmonella')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': '0.0.0.0',
        'PORT': '5432',
        'USER': 'blankuser', #CHANGE add postgres user
        'PASSWORD': 'blankpassword', #CHANGE add postgres password
        'NAME': 'default',
    },
    'clawclip': {
        "ENGINE": "django.db.backends.postgresql",
        "USER": 'blankuser',
        "PASSWORD": 'blankpassword',
        "HOST": "0.0.0.0",
        "PORT": "5432",
        'NAME': 'clawclip',
    },    
}

NONLOCALHOST='0.0.0.0' # leave as 0.0.0.0 for local install

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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

# added_on: 2018, Feb 8 - for HMAC activation workflow
ACCOUNT_ACTIVATION_DAYS = 7 # One-week activation window;
INCLUDE_REGISTER_URL = True
REGISTRATION_OPEN = True
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = False
DEFAULT_FROM_EMAIL = 'mgtdb@babs.unsw.edu.au'
LOGIN_REDIRECT_URL = '/'


# RELATIVE PATHS FROM folder containing manage.py in this repo to folder on your system
# NOTE: Please move the data folder to a secure place after setting up your databases.  
SUBDIR_REFERENCES = '.data/References/' 
SUBDIR_ALLELES = '.data/Alleles/' 
MEDIA_ROOT = '.data/Uploads/'
BLASTALLELES='.data/species_specific_alleles/'

# ABSOLUTE PATH VERSIONS OF ABOVE
ABS_SUBDIR_REFERENCES = 'data/References/'
ABS_SUBDIR_ALLELES = 'data/Alleles/' 
ABS_MEDIA_ROOT = "data/Uploads/" 
ABS_BLASTALLELES='data/species_specific_alleles/'

FILES_FOR_DOWNLOAD = "data/files_for_download/"
TMPFOLDER = "data/tmp_files/"

ASCPKEY = "/Path/to/.aspera/connect/etc/asperaweb_id_dsa.openssh" # CHANGE ONLY NEEDED IF RUNNING cron_pipeline --dl_reads

KRAKEN_DEFAULT_DB='/Path/to/folder/minikraken_20171013_4GB/'#CHANGE ONLY NEEDED IF RUNNING cron_pipeline --reads_to_alleles

### NOT NEEDED ON LOCAL DB ###
KATANA_LOCATION=''
TESTDB="True"
KATANA_SETTINGS=''
##############################

#CHANGE BELOW TO list species specific cutoffs/values
SPECIES_SEROVAR = {'Clawclip': {"species":'Blank species',
                                  "serovar":'',
                                  "min_largest_contig":60000,
                                  "max_contig_no":700,
                                  "n50_min":20000,
                                  "genome_min":4500000,
                                  "genome_max":5500000,
                                  "hspident":0.96,
                                  "locusnlimit":0.8,
                                  "snpwindow":40,
                                  "densitylim":4,
                                  "refsize":5.0,
                                  "blastident":90,
                                  "apzero":0.04
                                  }
                   }

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Australia/Sydney'

USE_I18N = True

USE_L10N = False

USE_TZ = True

DATE_FORMAT = 'Y-m-d'

STATIC_URL = '/static/'
STATIC_ROOT = 'Static/'

# CHANGE to extra columns in isolateList table or '' for default columns (i.e. 'Salmonella': '').
RAWQUERIES_DISPLAY = {'Clawclip': '', }  

