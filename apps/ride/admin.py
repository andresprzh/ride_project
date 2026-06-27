from django.contrib import admin

from apps.ride.models import Ride, RideEvent


@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'id_rider', 'id_driver', 'pickup_time')
    list_filter = ('status',)
    search_fields = ('id_rider__email', 'id_driver__email')
    raw_id_fields = ('id_rider', 'id_driver')


@admin.register(RideEvent)
class RideEventAdmin(admin.ModelAdmin):
    list_display = ('id', 'id_ride', 'description', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('description',)
    raw_id_fields = ('id_ride',)
