from rest_framework.viewsets import ModelViewSet

from apps.user.models import User
from apps.user.serializers import UserSerializer, UserWriteSerializer


class UserViewSet(ModelViewSet):
    """CRUD for users.

    Only users with the ``user`` role are exposed: they are the only ones
    that can be listed, retrieved, created, updated or deleted through this
    API. Admin accounts are never visible here (a request for one returns
    404), which also prevents them from being edited or deleted.
    """

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return UserWriteSerializer
        return UserSerializer

    def get_queryset(self):
        return User.objects.filter(role='user')
