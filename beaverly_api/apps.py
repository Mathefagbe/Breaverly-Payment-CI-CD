from django.apps import AppConfig


class BeaverlyApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "beaverly_api"

    def ready(self) -> None:
        from . import signals

        