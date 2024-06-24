from django.apps import AppConfig


class BeaverlyApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "beaverly_api"

    def ready(self) -> None:
        from . import signals
        from .role import add_permissions,add_role_permissions,add_roles

        add_roles()
        add_permissions()
        add_role_permissions()

        