from rest_framework import permissions, viewsets


class SuperAuthor(permissions.BasePermission):
    'allow read-only methods or author/superuser'
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS or request.user.is_superuser:
            return True
        return obj.user == request.user

class BaseViewSet(viewsets.ModelViewSet):
    permission_classes = [SuperAuthor]
    class Meta:
        abstract = True

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)
