from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import (
    Room, RoomImage, RoomAmenity, Service, ServiceDetail,
    Nationality, Booking, ServiceBooking, Payment, 
    RoomAvailability, Review, Contact, Notification
)

class RoomImageInline(admin.TabularInline):
    model = RoomImage
    extra = 1

class RoomAmenityInline(admin.TabularInline):
    model = RoomAmenity
    extra = 1

class ServiceDetailInline(admin.TabularInline):
    model = ServiceDetail
    extra = 1

class ServiceBookingInline(admin.TabularInline):
    model = ServiceBooking
    extra = 0
    readonly_fields = ('price_at_booking',)

class RoomAvailabilityInline(admin.TabularInline):
    model = RoomAvailability
    extra = 1

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'flag', 'is_active', 'total_rooms', 'available_rooms_count')
    list_filter = ('flag', 'is_active', 'price', 'created_at')
    search_fields = ('name', 'description')
    inlines = [RoomImageInline, RoomAmenityInline, RoomAvailabilityInline]
    prepopulated_fields = {'slug': ('name',)}
    
    def available_rooms_count(self, obj):
        return obj.available_rooms_count
    available_rooms_count.short_description = _('الغرف المتاحة حالياً')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_number', 'room', 'arrival_date', 'departure_date', 'status', 
                   'total_price', 'first_name', 'last_name')
    list_filter = ('status', 'room', 'arrival_date', 'departure_date', 'created_at')
    search_fields = ('booking_number', 'first_name', 'last_name', 'email', 'phone')
    date_hierarchy = 'arrival_date'
    inlines = [ServiceBookingInline]
    readonly_fields = ('booking_number', 'total_price', 'created_at', 'updated_at')

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'working_hours', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    inlines = [ServiceDetailInline]

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('name', 'room', 'rating', 'is_approved', 'created_at', 'comment_short')
    list_filter = ('rating', 'is_approved', 'created_at', 'room')
    search_fields = ('name', 'email', 'comment')
    actions = ['approve_reviews']
    
    def comment_short(self, obj):
        return obj.comment[:50] + '...' if len(obj.comment) > 50 else obj.comment
    comment_short.short_description = _('التعليق')
    
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
    approve_reviews.short_description = _('اعتماد التقييمات المحددة')

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'is_replied', 'created_at', 'message_short')
    list_filter = ('is_replied', 'subject', 'created_at')
    search_fields = ('name', 'email', 'message', 'reply_message')
    readonly_fields = ('created_at', 'replied_at')
    
    def message_short(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_short.short_description = _('الرسالة')

@admin.register(Nationality)
class NationalityAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('booking', 'amount', 'method', 'status', 'paid_at', 'transaction_id')
    list_filter = ('status', 'method', 'created_at')
    search_fields = ('booking__booking_number', 'transaction_id')
    readonly_fields = ('created_at', 'paid_at')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('subject', 'recipient_email', 'is_sent', 'sent_at', 'created_at')
    list_filter = ('is_sent', 'created_at')
    search_fields = ('subject', 'recipient_email', 'message')
    readonly_fields = ('created_at', 'sent_at')


admin.site.register(RoomImage)  
admin.site.register(RoomAmenity)  
admin.site.register(ServiceDetail)  
admin.site.register(ServiceBooking)  
admin.site.register(RoomAvailability)  