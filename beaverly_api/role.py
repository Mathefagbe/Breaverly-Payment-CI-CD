from .role_constant import default_role_permissions,default_roles
from beaverly_api import permissions as app_permissions
from .models import RolePermission,Roles,Permission

def add_roles():
    """Adds default roles to the Database"""
    for role in default_roles:
        try:
            Roles.objects.get(
                role=role["role"]
            )
        except Roles.DoesNotExist:
            Roles.objects.create(
                role=role["role"]
            )
        except Exception as e:
            print(e)


def add_permissions():
    """Adds default permissions to the Database"""
    # Permission.objects.all().delete()
    app_permissions_ = app_permissions.__dict__
    for permission in filter(lambda k: k[0] != "_", app_permissions_.keys()):
        try:
            Permission.objects.get(permission=permission)

        except Permission.DoesNotExist:
            Permission.objects.create(permission=permission)

        except Exception as e:
            print(e)


def add_role_permissions():
    """Adds default permissions for the default roles created to the database"""
    # RolePermission.objects.all().delete()
    for role_permission in default_role_permissions:
        for permission in role_permission["permissions"]:
            try:
                role = Roles.objects.get(
                    role=role_permission["role"],
                )
                perm = Permission.objects.get(
                    permission=permission
                )  # Get permission object
                RolePermission.objects.get(
                    role=role, permission=perm
                )  # Check if role with that permission exists

            except RolePermission.DoesNotExist:
                # If it doesn't exist, create new role permission
                RolePermission.objects.create(role=role, permission=perm)

            except Exception as e:
                print(e)