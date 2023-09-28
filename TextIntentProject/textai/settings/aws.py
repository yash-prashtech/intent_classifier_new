import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '1'
os.environ['TF_ENABLE_MKL_NATIVE_FORMAT'] = '1' 

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SITE_DOMAIN_LINK = 'https://intent.textdrip.ai/'

ALLOWED_HOSTS = ['*']

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
    
# if 'AWS_STORAGE_BUCKET_NAME' in os.environ:
#     STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
#     DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

#     AWS_STORAGE_BUCKET_NAME = os.environ['AWS_STORAGE_BUCKET_NAME']
#     AWS_S3_REGION_NAME = os.environ['AWS_S3_REGION_NAME']

#     AWS_S3_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
#     AWS_S3_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']

#     AWS_S3_ADDRESSING_STYLE = "virtual"


# set this to True to ensure cookies are only sent over HTTPS
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_TRUSTED_ORIGINS = ['https://intent.textdrip.ai']
