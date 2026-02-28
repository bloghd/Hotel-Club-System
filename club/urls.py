from django.urls import path
from .views import (
    club,
    facilities,
    facilities_booking,

)

app_name = 'club'

urlpatterns = [
    path('', club, name='club'),
    path('facilities/', facilities, name='facilities'),
    path('facilities-booking/', facilities_booking,name='facilities_booking'),
]