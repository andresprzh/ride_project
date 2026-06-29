from rest_framework import serializers

from apps.ride.models import Ride, RideEvent
from apps.user.models import User


class RideUserSerializer(serializers.ModelSerializer):
    """Lightweight user representation nested inside a Ride."""

    class Meta:
        model = User
        fields = ('id', 'role', 'first_name', 'last_name', 'email', 'phone_number')


class RideEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = RideEvent
        fields = ('id', 'id_ride', 'description', 'created_at')


class RideSerializer(serializers.ModelSerializer):
    """Full Ride representation including related rider, driver and events.

    On write, ``id_rider`` and ``id_driver`` accept user primary keys; on
    read they are expanded into the nested user objects.
    """

    rider = RideUserSerializer(source='id_rider', read_only=True)
    driver = RideUserSerializer(source='id_driver', read_only=True)
    today_ride_events = RideEventSerializer(many=True, read_only=True)

    class Meta:
        model = Ride
        fields = (
            'id',
            'status',
            'id_rider',
            'id_driver',
            'rider',
            'driver',
            'pickup_latitude',
            'pickup_longitude',
            'dropoff_latitude',
            'dropoff_longitude',
            'pickup_time',
            'today_ride_events',
        )
        extra_kwargs = {
            'id_rider': {'write_only': True},
            'id_driver': {'write_only': True},
        }
