from django.apps import AppConfig


class ScrappingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'scrapping'

    # def ready(self):
    #     from . import scheduler
    #     scheduler.start()
