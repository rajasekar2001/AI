import os
from pathlib import Path
from dotenv import load_dotenv

# --------------------------------------------------
# BASE DIRECTORY
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

# --------------------------------------------------
# LOAD ENV FILE
# --------------------------------------------------

load_dotenv(BASE_DIR / ".env")

# --------------------------------------------------
# API KEYS (FROM .env)
# --------------------------------------------------

HF_TOKEN = os.getenv("HF_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

print("DEBUG HF_TOKEN:", HF_TOKEN)
print("DEBUG GROQ_API_KEY:", GROQ_API_KEY)

# --------------------------------------------------
# SECURITY
# --------------------------------------------------

SECRET_KEY = 'django-insecure-your-key-here'
DEBUG = True
ALLOWED_HOSTS = []

# --------------------------------------------------
# INSTALLED APPS
# --------------------------------------------------

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'pgvector.django',
    'pgvector',

    'chatbot',  # Your app
]

# --------------------------------------------------
# MIDDLEWARE
# --------------------------------------------------

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# --------------------------------------------------
# URLS
# --------------------------------------------------

ROOT_URLCONF = 'core.urls'

# --------------------------------------------------
# TEMPLATES
# --------------------------------------------------

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [str(BASE_DIR / 'templates')],
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

# --------------------------------------------------
# DATABASE (POSTGRES LOCAL)
# --------------------------------------------------

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'supportbot',
        'USER': 'postgres',
        'PASSWORD': 'raja@2001',
        'HOST': 'localhost',
        'PORT': '5433',
    }
}

# --------------------------------------------------
# STATIC FILES
# --------------------------------------------------

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --------------------------------------------------
# AUTH REDIRECTS
# --------------------------------------------------

LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'landing'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
DATA_UPLOAD_MAX_MEMORY_SIZE = 104857600
FILE_UPLOAD_MAX_MEMORY_SIZE = 104857600

# import os
# from pathlib import Path
# from dotenv import load_dotenv

# BASE_DIR = Path(__file__).resolve().parent.parent
# load_dotenv(BASE_DIR / ".env")
# HF_TOKEN = os.getenv("HF_TOKEN")
# GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# print("DEBUG HF_TOKEN:", HF_TOKEN)
# # load_dotenv()
# # BASE_DIR = Path(__file__).resolve().parent.parent
# SECRET_KEY = 'django-insecure-your-key-here'
# DEBUG = True
# ALLOWED_HOSTS = []

# INSTALLED_APPS = [
#     'django.contrib.admin',
#     'django.contrib.auth',
#     'django.contrib.contenttypes',
#     'django.contrib.sessions',
#     'django.contrib.messages',
#     'django.contrib.staticfiles',
#     'pgvector.django',
#     'chatbot', # Your App
#     'pgvector', # Vector Support
# ]

# MIDDLEWARE = [
#     'django.middleware.security.SecurityMiddleware',
#     'django.contrib.sessions.middleware.SessionMiddleware',
#     'django.middleware.common.CommonMiddleware',
#     'django.middleware.csrf.CsrfViewMiddleware',
#     'django.contrib.auth.middleware.AuthenticationMiddleware',
#     'django.contrib.messages.middleware.MessageMiddleware',
#     'django.middleware.clickjacking.XFrameOptionsMiddleware',
# ]

# ROOT_URLCONF = 'core.urls'

# TEMPLATES = [
#     {
#         'BACKEND': 'django.template.backends.django.DjangoTemplates',
#         'DIRS': [str(BASE_DIR / 'templates')],
#         'APP_DIRS': True,
#         'OPTIONS': {
#             'context_processors': [
#                 'django.template.context_processors.debug',
#                 'django.template.context_processors.request',
#                 'django.contrib.auth.context_processors.auth',
#                 'django.contrib.messages.context_processors.messages',
#             ],
#         },
#     },
# ]

# # Database Setup for Supabase
# # DATABASES = {
# #     'default': {
# #         'ENGINE': 'django.db.backends.postgresql',
# #         'NAME': os.getenv('DB_NAME'),
# #         'USER': os.getenv('DB_USER'),
# #         'PASSWORD': os.getenv(''),
# #         'HOST': os.getenv('DB_HOST'),
# #         'PORT': os.getenv('DB_PORT'),
# #     }
# # }

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'supportbot',
#         'USER': 'postgres',
#         'PASSWORD': 'raja@2001',
#         'HOST': 'localhost',
#         'PORT': '5433',
#     }
# }

# STATIC_URL = 'static/'
# DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# # API Keys passed to the app
# GROQ_API_KEY = os.getenv("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")
# HF_TOKEN = os.getenv("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")

# LOGIN_REDIRECT_URL = 'dashboard'
# LOGOUT_REDIRECT_URL = 'landing'


# import os
# from pathlib import Path
# from dotenv import load_dotenv

# load_dotenv()
# BASE_DIR = Path(__file__).resolve().parent.parent
# SECRET_KEY = 'django-insecure-your-key-here'
# DEBUG = True
# ALLOWED_HOSTS = []

# INSTALLED_APPS = [
#     'django.contrib.admin',
#     'django.contrib.auth',
#     'django.contrib.contenttypes',
#     'django.contrib.sessions',
#     'django.contrib.messages',
#     'django.contrib.staticfiles',
#     'chatbot', # Your App
#     'pgvector', # Vector Support
# ]

# MIDDLEWARE = [
#     'django.middleware.security.SecurityMiddleware',
#     'django.contrib.sessions.middleware.SessionMiddleware',
#     'django.middleware.common.CommonMiddleware',
#     'django.middleware.csrf.CsrfViewMiddleware',
#     'django.contrib.auth.middleware.AuthenticationMiddleware',
#     'django.contrib.messages.middleware.MessageMiddleware',
#     'django.middleware.clickjacking.XFrameOptionsMiddleware',
# ]

# ROOT_URLCONF = 'core.urls'

# TEMPLATES = [
#     {
#         'BACKEND': 'django.template.backends.django.DjangoTemplates',
#         'DIRS': [str(BASE_DIR / 'templates')],
#         'APP_DIRS': True,
#         'OPTIONS': {
#             'context_processors': [
#                 'django.template.context_processors.debug',
#                 'django.template.context_processors.request',
#                 'django.contrib.auth.context_processors.auth',
#                 'django.contrib.messages.context_processors.messages',
#             ],
#         },
#     },
# ]

# # Database Setup for Supabase
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': os.getenv('voiceai'),
#         'USER': os.getenv('ai'),
#         'PASSWORD': os.getenv('12345'),
#         'HOST': os.getenv('localhost'),
#         'PORT': os.getenv('3306'),
#     }
# }

# STATIC_URL = 'static/'
# DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# # API Keys passed to the app
# GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# HF_TOKEN = os.getenv("HF_TOKEN")

# LOGIN_REDIRECT_URL = 'dashboard'
# LOGOUT_REDIRECT_URL = 'landing'


# import os
# from pathlib import Path
# from dotenv import load_dotenv

# load_dotenv()

# BASE_DIR = Path(__file__).resolve().parent.parent

# SECRET_KEY = 'django-insecure-your-key-here'
# DEBUG = True
# ALLOWED_HOSTS = []

# INSTALLED_APPS = [
#     'django.contrib.admin',
#     'django.contrib.auth',
#     'django.contrib.contenttypes',
#     'django.contrib.sessions',
#     'django.contrib.messages',
#     'django.contrib.staticfiles',
#     'chatbot',   # Your App
#     # ❌ Remove 'pgvector' if using MySQL
# ]

# MIDDLEWARE = [
#     'django.middleware.security.SecurityMiddleware',
#     'django.contrib.sessions.middleware.SessionMiddleware',
#     'django.middleware.common.CommonMiddleware',
#     'django.middleware.csrf.CsrfViewMiddleware',
#     'django.contrib.auth.middleware.AuthenticationMiddleware',
#     'django.contrib.messages.middleware.MessageMiddleware',
#     'django.middleware.clickjacking.XFrameOptionsMiddleware',
# ]

# ROOT_URLCONF = 'core.urls'

# TEMPLATES = [
#     {
#         'BACKEND': 'django.template.backends.django.DjangoTemplates',
#         'DIRS': [str(BASE_DIR / 'templates')],
#         'APP_DIRS': True,
#         'OPTIONS': {
#             'context_processors': [
#                 'django.template.context_processors.debug',
#                 'django.template.context_processors.request',
#                 'django.contrib.auth.context_processors.auth',
#                 'django.contrib.messages.context_processors.messages',
#             ],
#         },
#     },
# ]

# # ✅ MySQL Database Configuration
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'voiceai',        # Your MySQL database name
#         'USER': 'root',           # Your MySQL username
#         'PASSWORD': '12345',      # Your MySQL password
#         'HOST': '127.0.0.1',      # Usually localhost
#         'PORT': '3306',
#     }
# }

# STATIC_URL = 'static/'
# DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# # API Keys
# GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# HF_TOKEN = os.getenv("HF_TOKEN")

# LOGIN_REDIRECT_URL = 'dashboard'
# LOGOUT_REDIRECT_URL = 'landing'


# # import os
# # from pathlib import Path
# # from dotenv import load_dotenv

# # load_dotenv()
# # BASE_DIR = Path(__file__).resolve().parent.parent
# # SECRET_KEY = 'django-insecure-your-key-here'
# # DEBUG = True
# # ALLOWED_HOSTS = []

# # INSTALLED_APPS = [
# #     'django.contrib.admin',
# #     'django.contrib.auth',
# #     'django.contrib.contenttypes',
# #     'django.contrib.sessions',
# #     'django.contrib.messages',
# #     'django.contrib.staticfiles',
# #     'chatbot', # Your App
# #     'pgvector', # Vector Support
# # ]

# # MIDDLEWARE = [
# #     'django.middleware.security.SecurityMiddleware',
# #     'django.contrib.sessions.middleware.SessionMiddleware',
# #     'django.middleware.common.CommonMiddleware',
# #     'django.middleware.csrf.CsrfViewMiddleware',
# #     'django.contrib.auth.middleware.AuthenticationMiddleware',
# #     'django.contrib.messages.middleware.MessageMiddleware',
# #     'django.middleware.clickjacking.XFrameOptionsMiddleware',
# # ]

# # ROOT_URLCONF = 'core.urls'

# # TEMPLATES = [
# #     {
# #         'BACKEND': 'django.template.backends.django.DjangoTemplates',
# #         'DIRS': [str(BASE_DIR / 'templates')],
# #         'APP_DIRS': True,
# #         'OPTIONS': {
# #             'context_processors': [
# #                 'django.template.context_processors.debug',
# #                 'django.template.context_processors.request',
# #                 'django.contrib.auth.context_processors.auth',
# #                 'django.contrib.messages.context_processors.messages',
# #             ],
# #         },
# #     },
# # ]

# # # Database Setup for Supabase
# # DATABASES = {
# #     'default': {
# #         'ENGINE': 'django.db.backends.mysql',
# #         'NAME': os.getenv('voiceai'),
# #         'USER': os.getenv('ai'),
# #         'PASSWORD': os.getenv('12345'),
# #         'HOST': os.getenv('localhost'),
# #         'PORT': os.getenv('3306'),
# #     }
# # }

# # STATIC_URL = 'static/'
# # DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# # # API Keys passed to the app
# # GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# # HF_TOKEN = os.getenv("HF_TOKEN")

# # LOGIN_REDIRECT_URL = 'dashboard'
# # LOGOUT_REDIRECT_URL = 'landing'


