from rest_framework import permissions


class IsModerator(permissions.BasePermission):
    """Проверяет что пользователь в группе модераторов"""

    def has_permission(self, request, view):
        return request.user.groups.filter(name="moderators").exists()


class IsOwner(permissions.BasePermission):
    """Проверяет что пользователь - владелец объекта"""

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
