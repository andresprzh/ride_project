import pytest
from django.contrib.auth.models import AnonymousUser
from rest_framework.test import APIRequestFactory

from apps.user.models import User
from apps.user.permissions import IsAdminRole


class TestHasRole:
    """Unit tests for the User.has_role helper (no database needed)."""

    def test_returns_true_when_role_matches(self):
        user = User(role='admin')
        assert user.has_role('admin') is True

    def test_returns_false_when_role_differs(self):
        user = User(role='user')
        assert user.has_role('admin') is False


class TestIsAdminRole:
    """Tests for the IsAdminRole permission class."""

    def setup_method(self):
        self.permission = IsAdminRole()
        self.request = APIRequestFactory().get('/')

    def test_admin_user_is_allowed(self):
        self.request.user = User(role='admin', is_active=True)
        assert self.permission.has_permission(self.request, view=None) is True

    def test_non_admin_user_is_denied(self):
        self.request.user = User(role='user', is_active=True)
        assert self.permission.has_permission(self.request, view=None) is False

    def test_anonymous_user_is_denied(self):
        self.request.user = AnonymousUser()
        assert self.permission.has_permission(self.request, view=None) is False

    @pytest.mark.django_db
    def test_admin_user_from_database_is_allowed(self):
        user = User.objects.create_user(
            email='admin@example.com', password='pass1234', role='admin',
        )
        self.request.user = user
        assert self.permission.has_permission(self.request, view=None) is True

    @pytest.mark.django_db
    def test_regular_user_from_database_is_denied(self):
        user = User.objects.create_user(
            email='rider@example.com', password='pass1234', role='user',
        )
        self.request.user = user
        assert self.permission.has_permission(self.request, view=None) is False
