from django.db.models import ExpressionWrapper, F, FloatField
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView

from apps.ride.models import Ride
from apps.ride.serializers import RideSerializer


class RideListView(ListAPIView):
    """Return the list of rides (GET only).

    Supports:
      * pagination (project default ``BasePagination``)
      * filtering by ``status`` and by rider email (``rider_email``)
      * sorting by ``pickup_time`` or by distance to a given pickup GPS
        location, selected through the ``ordering`` query parameter.

    Related rider, driver and ride events are loaded with
    ``select_related``/``prefetch_related`` to keep the query count low.
    """

    serializer_class = RideSerializer

    def get_queryset(self):
        queryset = Ride.objects.select_related(
            'id_rider', 'id_driver',
        ).prefetch_related('ride_events')

        queryset = self._apply_filters(queryset)
        queryset = self._apply_ordering(queryset)
        return queryset

    def _apply_filters(self, queryset):
        params = self.request.query_params

        status = params.get('status')
        if status:
            queryset = queryset.filter(status=status)

        rider_email = params.get('rider_email')
        if rider_email:
            queryset = queryset.filter(id_rider__email=rider_email)

        return queryset

    def _apply_ordering(self, queryset):
        ordering = self.request.query_params.get('ordering', '-pickup_time')

        if ordering in ('pickup_time', '-pickup_time'):
            return queryset.order_by(ordering)

        if ordering in ('distance', '-distance'):
            return self._order_by_distance(queryset, descending=ordering.startswith('-'))

        raise ValidationError({
            'ordering': "Must be one of: 'pickup_time', '-pickup_time', 'distance', '-distance'.",
        })

    def _order_by_distance(self, queryset, descending):
        """Sort by squared Euclidean distance to the given pickup location.

        Distance is computed as a database expression so the sorting (and
        therefore pagination) happens entirely in SQL, never in Python.
        Squared distance is used because it preserves ordering while avoiding
        a SQRT, and works without any geospatial database extension.
        """
        lat = self._get_float_param('pickup_latitude')
        lng = self._get_float_param('pickup_longitude')

        distance = ExpressionWrapper(
            (F('pickup_latitude') - lat) * (F('pickup_latitude') - lat)
            + (F('pickup_longitude') - lng) * (F('pickup_longitude') - lng),
            output_field=FloatField(),
        )

        order = '-distance' if descending else 'distance'
        return queryset.annotate(distance=distance).order_by(order)

    def _get_float_param(self, name):
        value = self.request.query_params.get(name)
        if value is None:
            raise ValidationError({
                name: "This query parameter is required when ordering by distance.",
            })
        try:
            return float(value)
        except (TypeError, ValueError):
            raise ValidationError({name: 'Must be a valid number.'})
