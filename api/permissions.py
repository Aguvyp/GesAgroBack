from rest_framework.permissions import BasePermission


class IsSuperadmin(BasePermission):
    message = 'Esta operación requiere el rol Superadmin.'

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_active
            and request.user.rol == 'Superadmin'
        )
