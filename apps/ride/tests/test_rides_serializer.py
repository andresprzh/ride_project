import pytest
from django.utils import timezone

from apps.ride.models import RideEvent
from apps.ride.serializers import (
    RideEventSerializer,
    RideSerializer,
    RideUserSerializer,
)

pytestmark = pytest.mark.django_db


class TestRideUserSerializer:
    def test_contains_expected_user_fields(self, rider):
        data = RideUserSerializer(rider).data
        assert data == {
            'id': rider.id,
            'role': rider.role,
            'first_name': rider.first_name,
            'last_name': rider.last_name,
            'email': rider.email,
            'phone_number': rider.phone_number,
        }


class TestRideEventSerializer:
    def test_serializes_event_fields(self, make_ride):
        ride = make_ride()
        event = RideEvent.objects.create(
            id_ride=ride,
            description='Status changed to pickup',
            created_at=timezone.now(),
        )

        data = RideEventSerializer(event).data

        assert data['id'] == event.id
        assert data['id_ride'] == ride.id
        assert data['description'] == 'Status changed to pickup'
        assert 'created_at' in data


class TestRideSerializer:
    def test_read_includes_nested_rider_driver_and_events(self, make_ride, rider, driver):
        ride = make_ride(status='pickup')
        RideEvent.objects.create(
            id_ride=ride,
            description='Status changed to pickup',
            created_at=timezone.now(),
        )

        data = RideSerializer(ride).data

        assert data['id'] == ride.id
        assert data['status'] == 'pickup'
        assert data['rider']['email'] == rider.email
        assert data['driver']['email'] == driver.email
        assert len(data['ride_events']) == 1
        assert data['ride_events'][0]['description'] == 'Status changed to pickup'

    def test_id_rider_and_id_driver_are_write_only(self, make_ride):
        data = RideSerializer(make_ride()).data
        assert 'id_rider' not in data
        assert 'id_driver' not in data

    def test_create_ride_with_rider_and_driver_ids(self, rider, driver):
        payload = {
            'status': 'en-route',
            'id_rider': rider.id,
            'id_driver': driver.id,
            'pickup_latitude': 10.0,
            'pickup_longitude': 20.0,
            'dropoff_latitude': 11.0,
            'dropoff_longitude': 21.0,
            'pickup_time': timezone.now().isoformat(),
        }

        serializer = RideSerializer(data=payload)

        assert serializer.is_valid(), serializer.errors
        ride = serializer.save()
        assert ride.id_rider_id == rider.id
        assert ride.id_driver_id == driver.id
        assert ride.status == 'en-route'

    def test_invalid_status_is_rejected(self, rider, driver):
        payload = {
            'status': 'not-a-real-status',
            'id_rider': rider.id,
            'id_driver': driver.id,
            'pickup_latitude': 10.0,
            'pickup_longitude': 20.0,
            'dropoff_latitude': 11.0,
            'dropoff_longitude': 21.0,
            'pickup_time': timezone.now().isoformat(),
        }

        serializer = RideSerializer(data=payload)

        assert not serializer.is_valid()
        assert 'status' in serializer.errors
