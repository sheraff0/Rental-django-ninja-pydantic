import environ
import os, sys
from pathlib import Path
import re

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# used django environ 
# https://django-environ.readthedocs.io/en/latest/index.html
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))
env = environ.Env(DEBUG=(bool, False))

DEBUG = env.bool('DEBUG')
TOOLBAR = env.bool('TOOLBAR')
SILK = env.bool('SILK', False)
SWAGGER = env.bool('SWAGGER')
S3_STORAGE = env.bool('S3_STORAGE')
DAPHNE = env.bool('DAPHNE', False)

MEDIA_BASE_URL = env('MEDIA_BASE_URL')

TESTING_MODE = 'test' in sys.argv

REDIS_URL = env('REDIS_URL')
REDIS_HOST, REDIS_PORT = re.search(r"^.*//(.+):(\d+).*$", REDIS_URL).groups()
