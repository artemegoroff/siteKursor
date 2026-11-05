from django.apps import AppConfig


class VideosMigrationsConfig(AppConfig):
    name = 'videos'
    default_auto_field = 'django.db.models.AutoField'
    verbose_name = 'История миграций видеокурсов'
