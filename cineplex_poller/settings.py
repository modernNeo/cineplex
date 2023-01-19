import os

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
print(f"BASE_DIR={BASE_DIR}")

if os.environ['DOCKERIZED_DB'] == "true":
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ['POSTGRES_DB'],
            'USER': os.environ['POSTGRES_USER'],
            'PASSWORD': os.environ['POSTGRES_PASSWORD'],
            'HOST': f"{os.environ['COMPOSE_PROJECT_NAME']}_db",
            "PORT": "5432",
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / f'{os.environ["BOT_DATABASE_PATH"]}db.sqlite3',
        }
    }

print(f"DATABASES[default][NAME]={DATABASES['default']['NAME']}")

INSTALLED_APPS = (
    'cineplex',
)

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

TIME_ZONE = 'Canada/Pacific'

USE_TZ = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['SECRET_KEY']
