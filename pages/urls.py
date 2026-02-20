from django.urls import path
from .views import room_list, room_details, booking_step1, booking_step2, booking_step3, booking_confirmation, services


app_name = 'pages'

urlpatterns = [
    path('', room_list, name='room_list'),
    path('room-details/<slug:slug>/', room_details, name='room_details'),
    path('booking-step1/<slug:slug>/', booking_step1, name='booking_step1'),
    path('booking-step2/<slug:slug>/', booking_step2, name='booking_step2'),
    path('booking-step3/<slug:slug>/', booking_step3, name='booking_step3'),
    path('booking-confirmation/<str:booking_number>/', booking_confirmation, name='booking_confirmation'),
    path('services/', services, name='services'),
]