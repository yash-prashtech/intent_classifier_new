from pathlib import Path
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# from dotenv import load_dotenv
BASE_DIR = Path(__file__).resolve().parent.parent.parent
# load_dotenv(os.path.join(BASE_DIR,".env"))

SECRET_KEY = os.environ.get('SECRET_KEY', 'testiouuoisfjlaslkdfjlkasd)(*)(*!!@!213123123)')
DEBUG = True if int(os.environ.get('DEBUG', 1)) == 1 else False


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites', 
  
  
    'import_export',
    "crispy_forms",
    "crispy_bootstrap5",
    
    'accounts',
    'api',
    'core',
    'pdf_app',
    'intents_app',
    'smswebhook_app',
    
    'storages', #s3 bucket

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

ROOT_URLCONF = 'textai.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
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

WSGI_APPLICATION = 'textai.wsgi.application'

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

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


##################### CrispyTemplateSettings #########################
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"


################# Custom User Model + AllAuth ###################
AUTH_USER_MODEL = 'accounts.User'
SITE_ID = 1
DATA_UPLOAD_MAX_NUMBER_FIELDS = 100000

GLOBAL_TOKEN = str(os.environ.get('GLOBAL_TOKEN')).strip()


##################### Static and Media Files Settings #########################
STATIC_URL = '/static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
STATICFILES_DIRS = [BASE_DIR / "site_assets"]
STATIC_ROOT = BASE_DIR / "static_cdn" / "static" 
MEDIA_ROOT = BASE_DIR / "static_cdn" / "media" 

