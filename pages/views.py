from django.shortcuts import render, redirect, get_object_or_404
from .models import Room, RoomImage, RoomAmenity, Service, ServiceDetail, Booking, ServiceBooking
from django.contrib.auth.decorators import login_required
from .forms import BookingForm


def room_list(request):
    room_list = Room.objects.all()
    return render(request, 'pages/rooms.html', {'room_list': room_list})


def room_details(request, slug):
    room = get_object_or_404(Room, slug=slug)
    room_amenities = RoomAmenity.objects.filter(room=room)
    return render(request, 'pages/room_details.html', 
                  {
                      'room': room,
                      'room_amenities': room_amenities,
                  })

def booking(request, slug):
    room = get_object_or_404(Room, slug=slug, is_active=True)
    if request.method == 'POST':
        booking_form = BookingForm(request.POST)
        arrival_date = request.POST.get('arrival_date')
        departure_date = request.POST.get('departure_date')
        number_of_adults = request.POST.get('number_of_adults')
        number_of_children = request.POST.get('number_of_children')
        special_requests = request.POST.get('special_requests')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        nationality = request.POST.get('nationality')
        booking_number = request.POST.get('booking_number')
        email = request.POST.get('email')
        phone = request.POST.get('phone')

        if booking_form.is_valid():
            booking = booking_form.save(commit=False)
            booking.room = room
            booking.arrival_date = arrival_date
            booking.departure_date = departure_date
            booking.number_of_adults = number_of_adults
            booking.number_of_children = number_of_children
            booking.special_requests = special_requests
            booking.first_name = first_name
            booking.last_name = last_name
            booking.nationality = nationality
            booking.booking_number = booking_number
            booking.email = email
            booking.phone = phone
            booking.save()
            return redirect('pages:booking_success')
    return render(request, 'pages/booking.html',
                  {
                      'room': room
                  }
                  )
