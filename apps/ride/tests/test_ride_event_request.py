import pytest
from django.urls import reverse
from django.utils import timezone

from apps.ride.models import RideEvent

pytestmark = pytest.mark.django_db


@pytest.fixture
def list_url():
    return reverse('Rides:ride-event-list')


def detail_url(pk):
    return reverse('Rides:ride-event-detail', args=[pk])


class TestRideEventPermissions:
    def test_unauthenticated_request_is_rejected(self, api_client, list_url):
        assert api_client.get(list_url).status_code == 401

    def test_non_admin_user_is_forbidden(self, api_client, list_url, regular_user):
        api_client.force_authenticate(regular_user)
        assert api_client.get(list_url).status_code == 403


class TestRideEventCrud:
    def test_list(self, api_client, list_url, admin_user, make_ride):
        ride = make_ride()
        RideEvent.objects.create(
            id_ride=ride, description='Status changed to pickup',
            created_at=timezone.now(),
        )
        api_client.force_authenticate(admin_user)

        body = api_client.get(list_url).json()

        assert body['count'] == 1

    def test_create(self, api_client, list_url, admin_user, make_ride):
        ride = make_ride()
        api_client.force_authenticate(admin_user)
        payload = {
            'id_ride': ride.id,
            'description': 'Status changed to pickup',
            'created_at': timezone.now().isoformat(),
        }

        response = api_client.post(list_url, payload, format='json')

        assert response.status_code == 201
        assert RideEvent.objects.count() == 1
        assert response.json()['description'] == 'Status changed to pickup'

    def test_retrieve(self, api_client, admin_user, make_ride):
        ride = make_ride()
        event = RideEvent.objects.create(
            id_ride=ride, description='Status changed to pickup',
            created_at=timezone.now(),
        )
        api_client.force_authenticate(admin_user)

        body = api_client.get(detail_url(event.id)).json()

        assert body['id'] == event.id
        assert body['description'] == 'Status changed to pickup'

    def test_update(self, api_client, admin_user, make_ride):
        ride = make_ride()
        event = RideEvent.objects.create(
            id_ride=ride, description='old description',
            created_at=timezone.now(),
        )
        api_client.force_authenticate(admin_user)
        payload = {
            'id_ride': ride.id,
            'description': 'new description',
            'created_at': timezone.now().isoformat(),
        }

        response = api_client.put(detail_url(event.id), payload, format='json')

        assert response.status_code == 200
        event.refresh_from_db()
        assert event.description == 'new description'

    def test_delete(self, api_client, admin_user, make_ride):
        ride = make_ride()
        event = RideEvent.objects.create(
            id_ride=ride, description='Status changed to pickup',
            created_at=timezone.now(),
        )
        api_client.force_authenticate(admin_user)

        response = api_client.delete(detail_url(event.id))

        assert response.status_code == 204
        assert RideEvent.objects.count() == 0
