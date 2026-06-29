from rest_framework import serializers

from apps.user.models import User


class UserSerializer(serializers.ModelSerializer):
    """Read serializer for users. Never exposes the password."""

    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            'email',
            'phone_number',
        )


class UserWriteSerializer(serializers.ModelSerializer):
    """Write serializer for user create/update operations.

    Accepts a ``password`` (stored hashed) and is used only for write
    actions, so the password never appears in read responses.
    """

    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'password',
        )

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        # Users created through this API always have the 'user' role
        # (the model default is 'admin', so it must be set explicitly).
        user = User(role='user', **validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
