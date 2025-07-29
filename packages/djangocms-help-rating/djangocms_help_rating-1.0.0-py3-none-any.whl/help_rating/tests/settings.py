SECRET_KEY = "secret"

INSTALLED_APPS = (
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.sites",
    "cms",
    "menus",
    "treebeard",
    "help_rating",
)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "tests",
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LANGUAGE_CODE = "en"
LANGUAGES = (("en", "English"),)

SITE_ID = 1
USE_TZ = True

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "cms.middleware.page.CurrentPageMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "cms.context_processors.cms_settings",
            ],
            "loaders": ["django.template.loaders.filesystem.Loader", "django.template.loaders.app_directories.Loader"],
        },
    }
]

CMS_TEMPLATES = (("page.html", "Page"),)

CMS_CONFIRM_VERSION4 = True
