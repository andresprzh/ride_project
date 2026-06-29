import pytest
from django.urls import reverse

from apps.user.models import User

pytestmark = pytest.mark.django_db


@pytest.fixture
def list_url():
    return reverse('user:user-list')


def detail_url(pk):
    return reverse('user:user-detail', args=[pk])


class TestUserPermissions:
    def test_unauthenticated_request_is_rejected(self, api_client, list_url):
        assert api_client.get(list_url).status_code == 401

    def test_non_admin_user_is_forbidden(self, api_client, list_url, normal_user):
        api_client.force_authenticate(normal_user)
        assert api_client.get(list_url).status_code == 403


class TestUserListAndRetrieve:
    def test_only_role_user_accounts_are_listed(self, api_client, list_url, admin_user, normal_user):
        api_client.force_authenticate(admin_user)

        body = api_client.get(list_url).json()
        emails = [u['email'] for u in body['results']]

        assert normal_user.email in emails
        assert admin_user.email not in emails

    def test_password_and_role_are_not_in_response(self, api_client, admin_user, normal_user):
        api_client.force_authenticate(admin_user)

        body = api_client.get(detail_url(normal_user.id)).json()

        assert 'password' not in body
        assert 'role' not in body
        assert body['email'] == normal_user.email

    def test_retrieving_an_admin_returns_404(self, api_client, admin_user):
        other_admin = User.objects.create_user(
            email='admin2@example.com', password='pass1234', role='admin',
        )
        api_client.force_authenticate(admin_user)

        assert api_client.get(detail_url(other_admin.id)).status_code == 404


class TestUserCreate:
    def test_create_forces_role_user_and_hashes_password(self, api_client, list_url, admin_user):
        api_client.force_authenticate(admin_user)
        payload = {
            'email': 'new@example.com',
            'first_name': 'New',
            'password': 'secret123',
        }

        response = api_client.post(list_url, payload, format='json')

        assert response.status_code == 201
        assert 'password' not in response.json()
        created = User.objects.get(email='new@example.com')
        assert created.role == 'user'
        assert created.check_password('secret123')


class TestUserUpdateDelete:
    def test_delete_user(self, api_client, admin_user, normal_user):
        api_client.force_authenticate(admin_user)

        response = api_client.delete(detail_url(normal_user.id))

        assert response.status_code == 204
        assert not User.objects.filter(id=normal_user.id).exists()

    def test_cannot_delete_admin(self, api_client, admin_user):
        other_admin = User.objects.create_user(
            email='admin3@example.com', password='pass1234', role='admin',
        )
        api_client.force_authenticate(admin_user)

        response = api_client.delete(detail_url(other_admin.id))

        assert response.status_code == 404
        assert User.objects.filter(id=other_admin.id).exists()
