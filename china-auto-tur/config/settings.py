# В самом верху, после BASE_DIR
import os

# Добавляем наши приложения в список установленных
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # наши приложения
    "catalog",
    "orders",
    "accounts",
    "blog",
    "pages",
]

# База данных PostgreSQL
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "china_auto_tur",
        "USER": "postgres",
        "PASSWORD": "твой_пароль_от_postgres",  # поставь свой пароль
        "HOST": "localhost",
        "PORT": "5432",
    }
}

# Язык и часовой пояс
LANGUAGE_CODE = "ru-ru"
TIME_ZONE = "Europe/Moscow"

# Статические файлы (CSS, JS, картинки)
STATIC_URL = "/static/"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# Медиа-файлы (загрузки пользователей)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Шаблоны
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # общая папка шаблонов
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
