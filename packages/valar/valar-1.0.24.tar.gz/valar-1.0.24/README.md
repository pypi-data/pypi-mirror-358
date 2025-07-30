valar for morghulis

# settings
```python
from pathlib import Path

""" Compulsory settings """
DEBUG = True
BASE_DIR = Path(__file__).resolve().parent.parent
BASE_APP = str(BASE_DIR.name)
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


""" DataSource """

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

MONGO_SETTINGS = {
    'host': '47.98.192.120',
    'port': 27017,
    "username": "admin",
    "password": '19870120'
}

MINIO_SETTINGS = {
    'endpoint': '10.134.10.92:9000',
    'access_key': 'admin',
    "secret_key": "19870120",
    'secure': False
}

""" Minimized compulsory settings """

INSTALLED_APPS = [
    'django.contrib.sessions',
    "corsheaders",
    'channels',
    'valar.data'
]

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'valar.Middleware'
]

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
ROOT_URLCONF = "%s.urls" % BASE_APP
ASGI_APPLICATION = "%s.asgi.application" % BASE_APP
VALAR_CHANNEL_HANDLER_MAPPING = "%s.urls.channel_handler_mapping" % BASE_APP


""" Optional settings """
# ALLOWED_HOSTS = ['*']
# LANGUAGE_CODE = 'en-us'
# TIME_ZONE = 'Asia/Shanghai'
# USE_I18N = True
# USE_TZ = False
# SESSION_SAVE_EVERY_REQUEST = True
# SESSION_COOKIE_AGE = 60 * 60
# FILE_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024 * 100
# DATA_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024 * 100
```

# root urls
```python
from django.urls import path, include

from valar.channels import ValarSocketSender
from valar.channels.views import handel_channel

urlpatterns = [
    path('socket/<str:handler>', handel_channel),
    path('data/', include('valar.data.urls')),
]


channel_handler_mapping = {
    # 'test': test_handler
}

# async def test_handler(data, sender: ValarSocketSender):
#     # print(data, sender.handler, sender.client, sender.uid)
#     await sender.to_users({'user': 15}, 15)
#     for i in range(3):
#         await sender.to_clients({'h': i},sender.client)

```


# asgi
```python
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import re_path

from valar.channels import ValarConsumer

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
     'websocket': URLRouter([
        re_path(r'(?P<client>\w+)/$', ValarConsumer.as_asgi()),
    ])
})

```


