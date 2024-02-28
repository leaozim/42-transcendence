from django.apps import AppConfig


class SrcsMessageConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'srcs_message'

    def ready(self) -> None:
        import srcs_message.signals
