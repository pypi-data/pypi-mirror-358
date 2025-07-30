import importlib
import os

from django.apps import AppConfig
from django.conf import settings
from django.urls import include, path


class DataConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'src.valar.data'

    def ready(self):
        run_once = os.environ.get('CMDLINERUNNER_RUN_ONCE')
        if run_once is None:
            os.environ['CMDLINERUNNER_RUN_ONCE'] = 'True'
            root = settings.ROOT_URLCONF
            module = importlib.import_module(root)
            urlpatterns = getattr(module,'urlpatterns')



