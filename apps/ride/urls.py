from rest_framework.routers import DefaultRouter
from apps.ride.views import RideViewSet, RideEventViewSet

app_name = 'Rides'
router = DefaultRouter()
router.register('rides', RideViewSet, basename='ride')
router.register('ride-events', RideEventViewSet, basename='ride-event')

urlpatterns = router.urls