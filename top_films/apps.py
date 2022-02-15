from django.apps import AppConfig


class TopFilmsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'top_films'
    verbose_name = "Top 100 Films"
