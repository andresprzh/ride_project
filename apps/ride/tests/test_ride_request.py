from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from apps.ride.models import RideEvent
from apps.user.models import User

pytestmark = pytest.mark.django_db


@pytest.fixture
def url():
    return reverse('Rides:rides_list_view')


class TestRideListPermissions:
    def test_unauthenticated_request_is_rejected(self, api_client, url):
        response = api_client.get(url)
        assert response.status_code == 401

    def test_non_admin_user_is_forbidden(self, api_client, url, regular_user):
        api_client.force_authenticate(regular_user)
        response = api_client.get(url)
        assert response.status_code == 403

    def test_admin_user_is_allowed(self, api_client, url, admin_user, make_ride):
        make_ride()
        api_client.force_authenticate(admin_user)
        response = api_client.get(url)
        assert response.status_code == 200


class TestRideListContent:
    def test_response_is_paginated_with_nested_data(self, api_client, url, admin_user, make_ride):
        ride = make_ride()
        RideEvent.objects.create(
            id_ride=ride, description='Status changed to pickup',
            created_at=timezone.now(),
        )
        api_client.force_authenticate(admin_user)

        body = api_client.get(url).json()

        assert 'count' in body and 'results' in body
        assert body['count'] == 1
        result = body['results'][0]
        assert result['rider']['email'] == 'rider@example.com'
        assert result['driver']['email'] == 'driver@example.com'
        assert len(result['today_ride_events']) == 1


class TestTodayRideEvents:
    def test_only_events_from_last_24h_are_returned(self, api_client, url, admin_user, make_ride):
        ride = make_ride()
        RideEvent.objects.create(
            id_ride=ride, description='Status changed to pickup',
            created_at=timezone.now() - timedelta(hours=1),
        )
        RideEvent.objects.create(
            id_ride=ride, description='Old event outside the window',
            created_at=timezone.now() - timedelta(hours=48),
        )
        api_client.force_authenticate(admin_user)

        body = api_client.get(url).json()
        events = body['results'][0]['today_ride_events']

        assert len(events) == 1
        assert events[0]['description'] == 'Status changed to pickup'

    def test_ride_without_recent_events_returns_empty_list(self, api_client, url, admin_user, make_ride):
        ride = make_ride()
        RideEvent.objects.create(
            id_ride=ride, description='Old event',
            created_at=timezone.now() - timedelta(days=5),
        )
        api_client.force_authenticate(admin_user)

        body = api_client.get(url).json()

        assert body['results'][0]['today_ride_events'] == []


class TestRideListFiltering:
    def test_filter_by_status(self, api_client, url, admin_user, make_ride):
        make_ride(status='pickup')
        make_ride(status='dropoff')
        api_client.force_authenticate(admin_user)

        body = api_client.get(url, {'status': 'pickup'}).json()

        assert body['count'] == 1
        assert body['results'][0]['status'] == 'pickup'

    def test_filter_by_rider_email(self, api_client, url, admin_user, make_ride, rider):
        other_rider = User.objects.create_user(
            email='other@example.com', password='pass1234', role='user',
        )
        make_ride(id_rider=rider)
        make_ride(id_rider=other_rider)
        api_client.force_authenticate(admin_user)

        body = api_client.get(url, {'rider_email': rider.email}).json()

        assert body['count'] == 1
        assert body['results'][0]['rider']['email'] == rider.email


class TestRideListOrdering:
    def test_order_by_pickup_time_ascending(self, api_client, url, admin_user, make_ride):
        now = timezone.now()
        older = make_ride(pickup_time=now - timedelta(hours=2))
        newer = make_ride(pickup_time=now)
        api_client.force_authenticate(admin_user)

        body = api_client.get(url, {'ordering': 'pickup_time'}).json()

        assert [r['id'] for r in body['results']] == [older.id, newer.id]

    def test_order_by_distance_returns_closest_first(self, api_client, url, admin_user, make_ride):
        near = make_ride(pickup_latitude=0.0, pickup_longitude=0.0)
        far = make_ride(pickup_latitude=10.0, pickup_longitude=10.0)
        api_client.force_authenticate(admin_user)

        body = api_client.get(url, {
            'ordering': 'distance',
            'pickup_latitude': '0.1',
            'pickup_longitude': '0.1',
        }).json()

        assert [r['id'] for r in body['results']] == [near.id, far.id]

    def test_distance_ordering_without_coordinates_returns_400(self, api_client, url, admin_user):
        api_client.force_authenticate(admin_user)
        response = api_client.get(url, {'ordering': 'distance'})
        assert response.status_code == 400

    def test_invalid_ordering_returns_400(self, api_client, url, admin_user):
        api_client.force_authenticate(admin_user)
        response = api_client.get(url, {'ordering': 'banana'})
        assert response.status_code == 400
