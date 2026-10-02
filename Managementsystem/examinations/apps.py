from django.apps import AppConfig


class ExaminationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'examinations'

    def ready(self) -> None:
        import examinations.signals  # noqa: F401
