import pytest
from rest_framework.test import APIClient

from apps.user.models import User


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_user():
    return User.objects.create_user(
        email='admin@example.com', password='pass1234', role='admin',
    )


@pytest.fixture
def normal_user():
    return User.objects.create_user(
        email='user1@example.com', password='pass1234', role='user',
        first_name='Reg', last_name='User',
    )
