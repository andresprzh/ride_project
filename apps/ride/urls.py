from rest_framework.routers import DefaultRouter
from apps.ride.views import RideViewSet

app_name = 'Rides'
router = DefaultRouter()
router.register('rides', RideViewSet, basename='ride')

urlpatterns = router.urls