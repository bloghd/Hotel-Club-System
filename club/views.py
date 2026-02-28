from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Club, Workingoaches, MembershipPlans, Facility, FacilityBooking, FacilityServices

def club(request):
    clubs = Club.objects.filter(is_active=True)[:3]
    trainers = Workingoaches.objects.filter(is_active=True)[:3]
    membership_plans = MembershipPlans.objects.filter(is_active=True).prefetch_related('features')
    return render(request, 'club/club.html', 
                  {'clubs': clubs, 
                    'trainers': trainers,
                    'membership_plans': membership_plans
                                               })
def facilities(request):
    facilities = Facility.objects.filter(is_active=True).prefetch_related('services')
    return render(request, 'club/facilities.html', {'facilities': facilities})

def facilities_booking(request):
    facility_bookings  = get_object_or_404(FacilityBooking)
    if request.method == 'POST':
        facility = request.POST.get('facility')
        booking_date = request.POST.get('booking_date')
        booking_start_time = request.POST.get('booking_start_time')
        time_flag = request.POST.get('time_flag')
        FacilityBooking.objects.create(facility=facility, booking_date=booking_date, booking_start_time=booking_start_time, time_flag=time_flag)

        return HttpResponse("تم حجز المرفق بنجاح!")
    
    return render(request, 'club/facilities.html', {'facility_bookings': facility_bookings})