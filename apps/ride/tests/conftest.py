import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from apps.ride.models import Ride
from apps.user.models import User


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_user():
    return User.objects.create_user(
        email='admin@example.com', password='pass1234', role='admin',
        first_name='Ada', last_name='Min',
    )


@pytest.fixture
def regular_user():
    return User.objects.create_user(
        email='user@example.com', password='pass1234', role='user',
    )


@pytest.fixture
def rider():
    return User.objects.create_user(
        email='rider@example.com', password='pass1234', role='user',
        first_name='Riley', last_name='Rider', phone_number='111',
    )


@pytest.fixture
def driver():
    return User.objects.create_user(
        email='driver@example.com', password='pass1234', role='user',
        first_name='Dana', last_name='Driver', phone_number='222',
    )


@pytest.fixture
def make_ride(rider, driver):
    """Factory fixture to create rides with sensible defaults."""

    def _make(status='en-route', pickup_latitude=0.0, pickup_longitude=0.0,
              pickup_time=None, id_rider=None, id_driver=None):
        return Ride.objects.create(
            status=status,
            id_rider=id_rider or rider,
            id_driver=id_driver or driver,
            pickup_latitude=pickup_latitude,
            pickup_longitude=pickup_longitude,
            dropoff_latitude=1.0,
            dropoff_longitude=1.0,
            pickup_time=pickup_time or timezone.now(),
        )

    return _make
