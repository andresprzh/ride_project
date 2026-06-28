from django.urls import path
from apps.ride.views import RideListView

app_name = 'Rides'

urlpatterns = [
    path('Rides/', RideListView.as_view(), name='rides_list_view'),
]
