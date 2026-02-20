from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from datetime import datetime
from decimal import Decimal
from .models import Room, Booking, Payment, Nationality, PaymentStatus, RoomAmenity, Service, Contact
from django.core.mail import send_mail, BadHeaderError
from datetime import datetime
from smtplib import SMTPException

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

def booking_step1(request, slug):
    room = get_object_or_404(Room, slug=slug, is_active=True)
    
    if request.method == 'POST':
        request.session['booking_data'] = {
            'arrival_date': request.POST.get('arrival_date'),
            'departure_date': request.POST.get('departure_date'),
            'number_of_adults': request.POST.get('number_of_adults'),
            'number_of_children': request.POST.get('number_of_children'),
            'special_requests': request.POST.get('special_requests', ''),
        }
        return redirect('pages:booking_step2', slug=slug)
    
    return render(request, 'pages/booking_step1.html', {
        'room': room,
        'today': timezone.now()
    })


def booking_step2(request, slug):
    room = get_object_or_404(Room, slug=slug, is_active=True)
    
    if 'booking_data' not in request.session:
        return redirect('pages:booking_step1', slug=slug)
    
    if request.method == 'POST':

        request.session['booking_data'].update({
            'first_name': request.POST.get('first_name'),
            'last_name': request.POST.get('last_name'),
            'email': request.POST.get('email'),
            'phone': request.POST.get('phone'),
            'nationality': request.POST.get('nationality'),
        })
        request.session.modified = True
        return redirect('pages:booking_step3', slug=slug)
    
    return render(request, 'pages/booking_step2.html', {
        'room': room,
        'nationalities': Nationality.objects.all()
    })



def booking_step3(request, slug):
    room = get_object_or_404(Room, slug=slug, is_active=True)
    
    if 'booking_data' not in request.session:
        return redirect('pages:booking_step1', slug=slug)
    
    booking_data = request.session['booking_data']
    
    # حساب السعر
    arrival = datetime.strptime(booking_data['arrival_date'], '%Y-%m-%d').date()
    departure = datetime.strptime(booking_data['departure_date'], '%Y-%m-%d').date()
    nights = (departure - arrival).days
    total_price = nights * room.price
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # إنشاء الحجز
                booking = Booking.objects.create(
                    room=room,
                    arrival_date=arrival,
                    departure_date=departure,
                    number_of_adults=booking_data['number_of_adults'],
                    number_of_children=booking_data['number_of_children'],
                    special_requests=booking_data.get('special_requests', ''),
                    first_name=booking_data['first_name'],
                    last_name=booking_data['last_name'],
                    email=booking_data['email'],
                    phone=booking_data['phone'],
                    nationality_id=booking_data.get('nationality') or None,
                )
                
                # إنشاء الدفع
                payment_method = request.POST.get('payment_method', 'cash')
                Payment.objects.create(
                    booking=booking,
                    amount=total_price,
                    method=payment_method,
                    status=PaymentStatus.PENDING
                )
                
                # ==== إرسال الإيميل الجميل ====
                send_booking_email(booking, nights, total_price)
                
                # مسح الجلسة
                del request.session['booking_data']
                
                messages.success(request, 'تم تأكيد حجزك بنجاح!')
                return redirect('pages:booking_confirmation', booking_number=booking.booking_number)
                
        except Exception as e:
            messages.error(request, f'حدث خطأ: {str(e)}')
    
    return render(request, 'pages/booking_step3.html', {
        'room': room,
        'booking_data': booking_data,
        'nights': nights,
        'total_price': total_price
    })


def send_booking_email(booking, nights, total_price):
    
    subject = f'✅ تأكيد حجزك في Grand Royal | رقم الحجز: {booking.booking_number}'
    
    message = f"""
╔══════════════════════════════════════════════════════════════╗
║                    🏨 GRAND ROYAL HOTEL                      ║
║                      تأكيد الحجز                              ║
╚══════════════════════════════════════════════════════════════╝

أهلاً {booking.first_name} {booking.last_name} 👋

تم تأكيد حجزك بنجاح! إليك تفاصيل إقامتك:

┌─────────────────────────────────────────────────────────────┐
│ 📋 رقم الحجز: {booking.booking_number}
│ 🏠 الغرفة: {booking.room.name}
│ 💰 السعر/ليلة: {booking.room.price}$
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 📅 تاريخ الوصول:    {booking.arrival_date}
│ 📅 تاريخ المغادرة:   {booking.departure_date}
│ 🌙 عدد الليالي:     {nights} ليالي
│ 👨‍👩‍👧‍👦 الضيوف:          {booking.number_of_adults} بالغين, {booking.number_of_children} أطفال
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 💳 طريقة الدفع:     
│ 💵 الإجمالي:        {total_price}$  ⭐
└─────────────────────────────────────────────────────────────┘

📞 بيانات التواصل:
   • البريد: {booking.email}
   • الهاتف: {booking.phone}

╔══════════════════════════════════════════════════════════════╗
║  📍 العنوان: شارع الملك فهد، الرياض، المملكة العربية السعودية  ║
║  📞 الهاتف: +966 11 123 4567                                  ║
║  ✉️  البريد: info@grandroyal.com                              ║
╚══════════════════════════════════════════════════════════════╝

ننتظرك بفارغ الصبر! 🌟

مع تحيات فريق Grand Royal
    """
    
    # إرسال الإيميل
    try:
        sent = send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.email],
            fail_silently=False,  # False عشان نعرف لو فيه خطأ
        )
        # sent = 1 لو نجح، 0 لو فشل
        return sent > 0
        
    except BadHeaderError:
        print("❌ خطأ: عنوان الإيميل فيه مشكلة")
        return False
        
    except SMTPException as e:
        print(f"❌ خطأ SMTP: {str(e)}")
        return False
        
    except Exception as e:
        print(f"❌ خطأ عام في الإيميل: {str(e)}")
        return False


def booking_confirmation(request, booking_number):
    booking = get_object_or_404(Booking, booking_number=booking_number)
    nights = (booking.departure_date - booking.arrival_date).days
    total_price = booking.total_price or Decimal('0')
    tax_price =  15
    tax = total_price * tax_price
    service_fee = 12
    grand_total = total_price + tax + service_fee
    return render(request, 'pages/booking_confirmation.html', 
                  {'booking': booking,
                   'total_price': total_price,
                   'tax': tax,
                   'grand_total': grand_total,
                   'service_fee': service_fee,
                   'tax_price': tax_price,
                   'nights': nights
                   })

def services(request):
    services = Service.objects.filter(is_active=True).prefetch_related('details')
    context = {
        'services': services
    }
    return render(request, 'pages/services.html', context)


def contact(request):
    contact = get_object_or_404(Contact, is_active=True)
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('pages:contact')
    return render(request, 'pages/contact.html')

