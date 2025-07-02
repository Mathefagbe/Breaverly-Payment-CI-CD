from django.apps import AppConfig


class BeaverlyApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "beaverly_api"

    def ready(self) -> None:
        # from . import signals
        from .role import add_permissions,add_role_permissions,add_roles
        from .bank_helpers import load_banks

        add_roles()
        add_permissions()
        add_role_permissions()
        load_banks()

        