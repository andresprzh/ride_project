from django.conf import settings
from django.db import models


class Ride(models.Model):
    """A ride requested by a rider and served by a driver."""

    STATUS_CHOICES = [
        ('en-route', 'En route'),
        ('pickup', 'Pickup'),
        ('dropoff', 'Dropoff'),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        db_index=True,
    )
    id_rider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='rides_as_rider',
    )
    id_driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='rides_as_driver',
    )
    pickup_latitude = models.FloatField()
    pickup_longitude = models.FloatField()
    dropoff_latitude = models.FloatField()
    dropoff_longitude = models.FloatField()
    pickup_time = models.DateTimeField(db_index=True)

    class Meta:
        ordering = ['-pickup_time']

    def __str__(self):
        return f'Ride {self.pk} ({self.status})'


class RideEvent(models.Model):
    """An event in the lifecycle of a ride (e.g. status changes)."""

    id_ride = models.ForeignKey(
        Ride,
        on_delete=models.CASCADE,
        related_name='ride_events',
    )
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(db_index=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['id_ride', 'created_at']),
        ]

    def __str__(self):
        return f'RideEvent {self.pk} for ride {self.id_ride_id}'
