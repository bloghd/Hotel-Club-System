from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count, Sum, Avg
from django.utils.translation import gettext_lazy as _
from .models import (
    Room, RoomImage, RoomAmenity, Service, ServiceDetail,
    Nationality, Booking, ServiceBooking, Payment, 
    RoomAvailability, Review, Contact, Notification
)


# ============ INLINES ============

class RoomImageInline(admin.TabularInline):
    model = RoomImage
    extra = 1
    fields = ['image', 'is_primary', 'order', 'preview']
    readonly_fields = ['preview']
    
    def preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; border-radius: 4px;" />',
                obj.image.url
            )
        return "-"
    preview.short_description = _('معاينة')


class RoomAmenityInline(admin.TabularInline):
    model = RoomAmenity
    extra = 1
    fields = ['name', 'icon']


class ServiceDetailInline(admin.TabularInline):
    model = ServiceDetail
    extra = 1


class ServiceBookingInline(admin.TabularInline):
    model = ServiceBooking
    extra = 0
    readonly_fields = ['service', 'quantity', 'price_at_booking', 'booking_date']
    fields = ['service', 'quantity', 'price_at_booking', 'booking_date', 'scheduled_date']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False  # لا يمكن إضافة خدمات من هنا


class PaymentInline(admin.StackedInline):
    model = Payment
    extra = 0
    readonly_fields = ['created_at', 'paid_at']
    fields = [
        'amount', 'method', 'status', 
        'transaction_id', 'paid_at', 'created_at'
    ]


class RoomAvailabilityInline(admin.TabularInline):
    model = RoomAvailability
    extra = 7  # أسبوع كامل
    fields = ['date', 'available_count', 'price_override']


# ============ ADMIN CLASSES ============

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'price', 'capacity', 'total_rooms', 
        'flag_badge', 'is_active', 'available_count_display', 
        'created_at', 'main_image_preview'
    ]
    list_filter = ['flag', 'is_active', 'bed_type', 'created_at']
    search_fields = ['name', 'description', 'bed_type', 'size']
    list_editable = ['price', 'is_active']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        (_('معلومات أساسية'), {
            'fields': ('name', 'description', 'flag', 'is_active')
        }),
        (_('التسعير والسعة'), {
            'fields': ('price', 'total_rooms', 'capacity')
        }),
        (_('التفاصيل'), {
            'fields': ('bed_type', 'size', 'image')
        }),
        (_('تواريخ'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'main_image_preview']
    
    inlines = [RoomImageInline, RoomAmenityInline, RoomAvailabilityInline]
    
    actions = ['make_available', 'make_vip', 'make_not_available', 'duplicate_room']
    
    # ✅ إحصائيات في أعلى الصفحة
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            bookings_count=Count('bookings'),
            total_revenue=Sum('bookings__total_price')
        )
    
    def flag_badge(self, obj):
        colors = {
            'available': 'green',
            'not_available': 'red',
            'vip': 'purple',
            'most_requested': 'orange'
        }
        color = colors.get(obj.flag, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 12px; font-size: 12px;">{}</span>',
            color, obj.get_flag_display()
        )
    flag_badge.short_description = _('الحالة')
    
    def main_image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 60px; border-radius: 8px; '
                'box-shadow: 0 2px 4px rgba(0,0,0,0.1);" />',
                obj.image.url
            )
        return format_html(
            '<div style="width: 60px; height: 60px; background: #f0f0f0; '
            'border-radius: 8px; display: flex; align-items: center; '
            'justify-content: center; color: #999;">لا توجد</div>'
        )
    main_image_preview.short_description = _('الصورة')
    
    def available_count_display(self, obj):
        count = obj.available_rooms_count
        total = obj.total_rooms
        percentage = (count / total * 100) if total > 0 else 0
        
        if percentage > 50:
            color = 'green'
        elif percentage > 20:
            color = 'orange'
        else:
            color = 'red'
            
        return format_html(
            '<span style="color: {};">{} / {} ({}%)</span>',
            color, count, total, int(percentage)
        )
    available_count_display.short_description = _('المتاح')
    
    # ✅ Actions مخصصة
    @admin.action(description=_('تعيين كـ متاحة'))
    def make_available(self, request, queryset):
        queryset.update(flag=Room.RoomFlag.AVAILABLE)
        self.message_user(request, _('تم تحديث الحالة إلى متاحة'))
    
    @admin.action(description=_('تعيين كـ VIP'))
    def make_vip(self, request, queryset):
        queryset.update(flag=Room.RoomFlag.VIP)
        self.message_user(request, _('تم تحديث الحالة إلى VIP'))
    
    @admin.action(description=_('تعيين كـ غير متاحة'))
    def make_not_available(self, request, queryset):
        queryset.update(flag=Room.RoomFlag.NOT_AVAILABLE)
        self.message_user(request, _('تم تحديث الحالة إلى غير متاحة'))
    
    @admin.action(description=_('نسخ الغرف المختارة'))
    def duplicate_room(self, request, queryset):
        for room in queryset:
            room.pk = None
            room.name = f"{room.name} (نسخة)"
            room.save()
        self.message_user(request, _('تم نسخ {} غرفة').format(len(queryset)))


@admin.register(RoomImage)
class RoomImageAdmin(admin.ModelAdmin):
    list_display = ['room', 'preview', 'is_primary', 'order']
    list_filter = ['is_primary', 'room']
    list_editable = ['is_primary', 'order']
    search_fields = ['room__name']
    
    def preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 80px; border-radius: 4px;" />',
                obj.image.url
            )
        return "-"
    preview.short_description = _('معاينة')


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'working_hours', 'is_active', 'image_preview']
    list_filter = ['is_active', 'created_at']
    list_editable = ['price', 'is_active']
    search_fields = ['name', 'description']
    inlines = [ServiceDetailInline]
    
    def image_preview(self, obj):
        if obj.servicesimage:
            return format_html(
                '<img src="{}" style="max-height: 50px; border-radius: 4px;" />',
                obj.servicesimage.url
            )
        return "-"
    image_preview.short_description = _('الصورة')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = [
        'booking_number', 'room', 'guest_info', 
        'dates', 'nights_count', 'total_price', 
        'payment_status', 'created_at'
    ]
    list_filter = [
        'status', 'arrival_date', 'departure_date',
        'room__name', 'created_at'
    ]
    search_fields = [
        'booking_number', 'first_name', 'last_name', 
        'email', 'phone'
    ]
    date_hierarchy = 'arrival_date'
    ordering = ['-created_at']
    
    fieldsets = (
        (_('معلومات الحجز'), {
            'fields': ('booking_number', 'room', 'status')
        }),
        (_('التواريخ'), {
            'fields': ('arrival_date', 'departure_date', 'number_of_nights')
        }),
        (_('معلومات الضيف'), {
            'fields': (
                ('first_name', 'last_name'),
                'email', 'phone', 'nationality'
            )
        }),
        (_('التفاصيل'), {
            'fields': ('number_of_adults', 'number_of_children', 'special_requests')
        }),
        (_('المالية'), {
            'fields': ('total_price',),
            'classes': ('collapse',)
        }),
        (_('التواريخ'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = [
        'booking_number', 'number_of_nights', 
        'total_price', 'created_at', 'updated_at'
    ]
    
    inlines = [ServiceBookingInline, PaymentInline]
    
    actions = ['confirm_bookings', 'cancel_bookings', 'send_confirmation_email']
    
    def guest_info(self, obj):
        return format_html(
            '<strong>{} {}</strong><br>'
            '<small style="color: #666;">{}</small><br>'
            '<small style="color: #999;">{}</small>',
            obj.first_name, obj.last_name,
            obj.email,
            obj.phone
        )
    guest_info.short_description = _('الضيف')
    
    def dates(self, obj):
        return format_html(
            '<span style="direction: ltr; display: block;">'
            '{} → {}</span>',
            obj.arrival_date.strftime('%Y-%m-%d'),
            obj.departure_date.strftime('%Y-%m-%d')
        )
    dates.short_description = _('التواريخ')
    
    def nights_count(self, obj):
        nights = obj.number_of_nights
        return format_html(
            '<span style="background: #e3f2fd; padding: 2px 8px; '
            'border-radius: 12px; font-size: 12px;">{} ليلة</span>',
            nights
        )
    nights_count.short_description = _('الليالي')
    
    def payment_status(self, obj):
        try:
            payment = obj.payment
            colors = {
                'pending': 'orange',
                'completed': 'green',
                'failed': 'red',
                'refunded': 'gray'
            }
            color = colors.get(payment.status, 'black')
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}</span><br>'
                '<small>{}</small>',
                color,
                payment.get_status_display(),
                payment.get_method_display()
            )
        except Payment.DoesNotExist:
            return format_html(
                '<span style="color: red;">لا يوجد دفع</span>'
            )
    payment_status.short_description = _('الدفع')
    
    # ✅ Actions
    @admin.action(description=_('تأكيد الحجوزات المختارة'))
    def confirm_bookings(self, request, queryset):
        queryset.update(status='confirmed')
        self.message_user(request, _('تم تأكيد {} حجز').format(queryset.count()))
    
    @admin.action(description=_('إلغاء الحجوزات المختارة'))
    def cancel_bookings(self, request, queryset):
        queryset.update(status='cancelled')
        self.message_user(request, _('تم إلغاء {} حجز').format(queryset.count()))
    
    @admin.action(description=_('إرسال إيميل التأكيد'))
    def send_confirmation_email(self, request, queryset):
        # هنا تضيف logic إرسال الإيميل
        for booking in queryset:
            Notification.objects.create(
                booking=booking,
                recipient_email=booking.email,
                subject=_('تأكيد حجزك - {}').format(booking.booking_number),
                message=_('تم تأكيد حجزك بنجاح...')
            )
        self.message_user(request, _('تم إنشاء إشعارات التأكيد'))


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'booking_link', 'amount', 'method', 'status', 'status_colored',
        'status_colored', 'transaction_id', 'paid_at'
    ]
    list_filter = ['status', 'method', 'created_at']
    list_editable = ['status']
    search_fields = ['booking__booking_number', 'transaction_id']
    date_hierarchy = 'created_at'
    
    def booking_link(self, obj):
        url = reverse('admin:appname_booking_change', args=[obj.booking.id])
        return format_html(
            '<a href="{}" style="font-weight: bold;">{}</a>',
            url, obj.booking.booking_number
        )
    booking_link.short_description = _('الحجز')
    
    def status_colored(self, obj):
        colors = {
            'pending': '#ff9800',
            'completed': '#4caf50',
            'failed': '#f44336',
            'refunded': '#9e9e9e'
        }
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 4px 12px; border-radius: 4px; font-weight: bold;">'
            '{}</span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display()
        )
    status_colored.short_description = _('الحالة')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = [
        'room', 'name', 'rating_stars', 
        'is_approved', 'created_at', 'short_comment'
    ]
    list_filter = ['is_approved', 'rating', 'created_at', 'room']
    list_editable = ['is_approved']
    search_fields = ['name', 'email', 'comment']
    actions = ['approve_reviews', 'reject_reviews']
    
    def rating_stars(self, obj):
        stars = '⭐' * obj.rating
        return format_html(
            '<span style="font-size: 16px; letter-spacing: 2px;">{}</span>',
            stars
        )
    rating_stars.short_description = _('التقييم')
    
    def short_comment(self, obj):
        return obj.comment[:50] + '...' if len(obj.comment) > 50 else obj.comment
    short_comment.short_description = _('التعليق')
    
    @admin.action(description=_('اعتماد التقييمات'))
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
    
    @admin.action(description=_('رفض التقييمات'))
    def reject_reviews(self, request, queryset):
        queryset.update(is_approved=False)


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'email', 'phone', 'subject', 
        'is_replied_colored', 'created_at', 'message_preview'
    ]
    list_filter = ['subject', 'is_replied', 'created_at']
    search_fields = ['name', 'email', 'message']
    readonly_fields = ['created_at']
    
    fieldsets = (
        (_('معلومات المرسل'), {
            'fields': ('name', 'email', 'phone')
        }),
        (_('الرسالة'), {
            'fields': ('subject', 'message')
        }),
        (_('الرد'), {
            'fields': ('is_replied', 'replied_at', 'reply_message'),
            'classes': ('wide',)
        }),
        (_('تاريخ الإرسال'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def is_replied_colored(self, obj):
        if obj.is_replied:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ تم الرد</span>'
            )
        return format_html(
            '<span style="color: orange; font-weight: bold;">⏳ بانتظار الرد</span>'
        )
    is_replied_colored.short_description = _('حالة الرد')
    
    def message_preview(self, obj):
        return obj.message[:60] + '...' if len(obj.message) > 60 else obj.message
    message_preview.short_description = _('نص الرسالة')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        'subject', 'recipient_email', 'is_sent', 
        'sent_at', 'created_at', 'booking_link'
    ]
    list_filter = ['is_sent', 'created_at']
    search_fields = ['subject', 'recipient_email', 'message']
    actions = ['resend_notifications']
    
    def booking_link(self, obj):
        if obj.booking:
            url = reverse('admin:appname_booking_change', args=[obj.booking.id])
            return format_html('<a href="{}">{}</a>', url, obj.booking.booking_number)
        return "-"
    booking_link.short_description = _('الحجز')
    
    @admin.action(description=_('إعادة إرسال الإشعارات'))
    def resend_notifications(self, request, queryset):
        queryset.update(is_sent=False, sent_at=None)
        self.message_user(request, _('تم إعادة تعيين الإشعارات للإرسال'))


# ✅ تسجيل الباقي بشكل بسيط أو مخصص
@admin.register(RoomAmenity)
class RoomAmenityAdmin(admin.ModelAdmin):
    list_display = ['name', 'room', 'icon']
    list_filter = ['room']
    search_fields = ['name']


@admin.register(ServiceDetail)
class ServiceDetailAdmin(admin.ModelAdmin):
    list_display = ['name', 'service']
    search_fields = ['name', 'service__name']


@admin.register(Nationality)
class NationalityAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'bookings_count']
    search_fields = ['name', 'code']
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            bookings_count=Count('bookings')
        )
    
    def bookings_count(self, obj):
        return obj.bookings_count
    bookings_count.short_description = _('عدد الحجوزات')


@admin.register(RoomAvailability)
class RoomAvailabilityAdmin(admin.ModelAdmin):
    list_display = ['room', 'date', 'available_count', 'price_override']
    list_filter = ['room', 'date']
    date_hierarchy = 'date'
    list_editable = ['available_count', 'price_override']


@admin.register(ServiceBooking)
class ServiceBookingAdmin(admin.ModelAdmin):
    list_display = [
        'service', 'booking_link', 'quantity', 
        'price_at_booking', 'scheduled_date'
    ]
    list_filter = ['service', 'booking_date']
    search_fields = ['service__name', 'booking__booking_number']
    
    def booking_link(self, obj):
        url = reverse('admin:appname_booking_change', args=[obj.booking.id])
        return format_html('<a href="{}">{}</a>', url, obj.booking.booking_number)
    booking_link.short_description = _('الحجز')


# ✅ لوحة تحكم مخصصة (Dashboard)
from django.shortcuts import render
from django.db.models import Count, Sum, Avg, Q
from datetime import datetime, timedelta

def admin_dashboard(request):
    """لوحة تحكم مخصصة للإحصائيات"""
    today = datetime.now().date()
    this_month = today.replace(day=1)
    
    context = {
        'total_rooms': Room.objects.count(),
        'active_bookings': Booking.objects.filter(
            departure_date__gte=today,
            status='confirmed'
        ).count(),
        'today_arrivals': Booking.objects.filter(
            arrival_date=today
        ).count(),
        'today_departures': Booking.objects.filter(
            departure_date=today
        ).count(),
        'month_revenue': Payment.objects.filter(
            status='completed',
            paid_at__gte=this_month
        ).aggregate(Sum('amount'))['amount__sum'] or 0,
        'pending_contacts': Contact.objects.filter(is_replied=False).count(),
        'latest_reviews': Review.objects.filter(is_approved=False)[:5],
        'occupancy_rate': calculate_occupancy_rate(),
    }
    return render(request, 'admin/dashboard.html', context)

def calculate_occupancy_rate():
    """حساب نسبة الإشغال"""
    today = datetime.now().date()
    total_rooms = Room.objects.filter(is_active=True).aggregate(
        total=Sum('total_rooms')
    )['total'] or 0
    
    if total_rooms == 0:
        return 0
    
    occupied = Booking.objects.filter(
        arrival_date__lte=today,
        departure_date__gt=today,
        status='confirmed'
    ).count()
    
    return (occupied / total_rooms) * 100