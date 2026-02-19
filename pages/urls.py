from django.urls import path
from .views import room_list, room_details, booking


app_name = 'pages'

urlpatterns = [
    path('', room_list, name='room_list'),
    path('room-details/<slug:slug>/', room_details, name='room_details'),
    path('room-details/<slug:slug>/booking', booking, name='booking'),
]