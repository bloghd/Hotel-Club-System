from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, EmailValidator
from django.core.exceptions import ValidationError
import datetime


class RoomFlag(models.TextChoices):
    AVAILABLE = 'available', _('متاحة')
    NOT_AVAILABLE = 'not_available', _('غير متاحة')
    VIP = 'vip', _('VIP')
    MOST_REQUESTED = 'most_requested', _('الأكثر طلباً')


class SubjectFlag(models.TextChoices):
    BOOKING_INQUIRY = 'booking_inquiry', _('استفسار حجز')
    SPORTS_CLUB = 'sports_club', _('النادي الرياضي')
    COMPLAINT = 'complaint', _('شكوى')
    SUGGESTION = 'suggestion', _('اقتراح')
    OTHER = 'other', _('أخرى')


class PaymentStatus(models.TextChoices):
    PENDING = 'pending', _('معلق')
    COMPLETED = 'completed', _('مكتمل')
    FAILED = 'failed', _('فاشل')
    REFUNDED = 'refunded', _('مسترد')


class PaymentMethod(models.TextChoices):
    CASH = 'cash', _('كاش')
    CREDIT_CARD = 'credit_card', _('بطاقة ائتمان')
    BANK_TRANSFER = 'bank_transfer', _('تحويل بنكي')
    ONLINE = 'online', _('دفع إلكتروني')


# ============ MODELS ============
class Room(models.Model):
    name = models.CharField(_('الاسم'), max_length=100, unique=True)
    description = models.TextField(_('الوصف'))
    price = models.DecimalField(
        _('السعر لليلة'), 
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(_('الصورة الرئيسية'), upload_to='rooms/', null=True, blank=True)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), default=timezone.now)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)
    total_rooms = models.PositiveIntegerField(_('إجمالي عدد الغرف'), default=1)
    capacity = models.PositiveIntegerField(_('السعة (عدد الأشخاص)'), default=2)
    bed_type = models.CharField(_('نوع السرير'), max_length=100)
    size = models.CharField(_('المساحة'), max_length=100, help_text=_('مثال: 30 م²'))

    flag = models.CharField(
        _('الحالة'),
        max_length=20,
        choices=RoomFlag.choices,
        default=RoomFlag.AVAILABLE
    )
    is_active = models.BooleanField(_('نشط'), default=True)

    class Meta:
        verbose_name = _('غرفة')
        verbose_name_plural = _('الغرف')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['flag']),
            models.Index(fields=['price']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_flag_display()})"

    def clean(self):
        if self.total_rooms < 1:
            raise ValidationError(_('يجب أن يكون عدد الغرف على الأقل 1'))

    @property
    def available_rooms_count(self):
        booked = self.bookings.filter(
            departure_date__gte=timezone.now().date(),
            payment__status=PaymentStatus.COMPLETED
        ).count()
        return max(0, self.total_rooms - booked)


class RoomImage(models.Model):
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_('الغرفة')
    )
    image = models.ImageField(_('الصورة'), upload_to='rooms/gallery/')
    is_primary = models.BooleanField(_('صورة رئيسية'), default=False)
    order = models.PositiveIntegerField(_('الترتيب'), default=0)

    class Meta:
        verbose_name = _('صورة غرفة')
        verbose_name_plural = _('صور الغرف')
        ordering = ['order']

    def __str__(self):
        return f"صورة {self.room.name}"


class RoomAmenity(models.Model):
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='amenities',
        verbose_name=_('الغرفة')
    )
    name = models.CharField(_('الاسم'), max_length=100)
    icon = models.CharField(_('الأيقونة'), max_length=50, blank=True, help_text=_('Font Awesome class'))

    class Meta:
        verbose_name = _('ميزة الغرفة')
        verbose_name_plural = _('ميزات الغرف')
        unique_together = ('room', 'name')

    def __str__(self):
        return f"{self.name} - {self.room.name}"


class Service(models.Model):
    name = models.CharField(_('الاسم'), max_length=100, unique=True)
    description = models.TextField(_('الوصف'))
    image = models.ImageField(_('الصورة'), upload_to='services/', null=True, blank=True)
    price = models.DecimalField(
        _('السعر'), 
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    working_hours = models.CharField(_('ساعات العمل'), max_length=100)
    is_active = models.BooleanField(_('نشط'), default=True)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), default=timezone.now)

    class Meta:
        verbose_name = _('خدمة')
        verbose_name_plural = _('الخدمات')
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class ServiceDetail(models.Model):
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='details',
        verbose_name=_('الخدمة')
    )
    name = models.CharField(_('التفصيل'), max_length=100)
    description = models.TextField(_('وصف إضافي'), blank=True)

    class Meta:
        verbose_name = _('تفصيل الخدمة')
        verbose_name_plural = _('تفاصيل الخدمات')
        unique_together = ('service', 'name')

    def __str__(self):
        return f"{self.name} - {self.service.name}"


class Nationality(models.Model):
    name = models.CharField(_('الاسم'), max_length=100, unique=True)
    code = models.CharField(_('الكود'), max_length=3, blank=True)

    class Meta:
        verbose_name = _('جنسية')
        verbose_name_plural = _('الجنسيات')
        ordering = ['name']

    def __str__(self):
        return self.name


class Booking(models.Model):
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name="bookings",
        verbose_name=_("الغرفة")
    )
    booking_number = models.CharField(_('رقم الحجز'), max_length=20, unique=True, blank=True)
    
    arrival_date = models.DateField(_("تاريخ الوصول"))
    departure_date = models.DateField(_("تاريخ المغادرة"))
    number_of_adults = models.PositiveIntegerField(_("عدد البالغين"), default=1)
    number_of_children = models.PositiveIntegerField(_("عدد الأطفال"), default=0)
    special_requests = models.TextField(_("طلبات خاصة"), blank=True, null=True)
    first_name = models.CharField(_("الاسم الأول"), max_length=100)
    last_name = models.CharField(_("الاسم الأخير"), max_length=100)
    email = models.EmailField(_("البريد الإلكتروني"))
    phone = models.CharField(_("رقم الهاتف"), max_length=20)
    
    nationality = models.ForeignKey(
        Nationality,
        on_delete=models.SET_NULL,
        related_name="bookings",
        verbose_name=_("الجنسية"),
        blank=True,
        null=True
    )
    status = models.CharField(_('الحالة'), max_length=20, default='confirmed')
    total_price = models.DecimalField(_('إجمالي السعر'), max_digits=12, decimal_places=2, null=True, blank=True)
    
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), default=timezone.now)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)

    class Meta:
        verbose_name = _("حجز")
        verbose_name_plural = _("الحجوزات")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=['booking_number']),
            models.Index(fields=['arrival_date', 'departure_date']),
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return f"{self.booking_number or self.id} - {self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if not self.booking_number:
            self.booking_number = self.generate_booking_number()
        if not self.total_price:
            nights = (self.departure_date - self.arrival_date).days
            self.total_price = self.room.price * nights
        
        super().save(*args, **kwargs)

    def generate_booking_number(self):
        import random
        import string
        prefix = "BK"
        suffix = ''.join(random.choices(string.digits, k=6))
        return f"{prefix}{timezone.now().strftime('%y%m')}{suffix}"

    def clean(self):
        if self.departure_date <= self.arrival_date:
            raise ValidationError(_('تاريخ المغادرة يجب أن يكون بعد تاريخ الوصول'))
        
        if self.arrival_date < timezone.now().date():
            raise ValidationError(_('تاريخ الوصول لا يمكن أن يكون في الماضي'))
        
        if not self.pk:  
            overlapping = Booking.objects.filter(
                room=self.room,
                status='confirmed',
                arrival_date__lt=self.departure_date,
                departure_date__gt=self.arrival_date
            ).count()
            
            if overlapping >= self.room.total_rooms:
                raise ValidationError(_('لا توجد غرف متاحة في هذه الفترة'))

    @property
    def number_of_nights(self):
        return (self.departure_date - self.arrival_date).days


class ServiceBooking(models.Model):
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='service_bookings',
        verbose_name=_('الحجز')
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name=_('الخدمة')
    )
    quantity = models.PositiveIntegerField(_('الكمية'), default=1)
    booking_date = models.DateTimeField(_('تاريخ الحجز'), default=timezone.now)
    scheduled_date = models.DateTimeField(_('الموعد المحدد'), null=True, blank=True)
    notes = models.TextField(_('ملاحظات'), blank=True)
    price_at_booking = models.DecimalField(_('السعر وقت الحجز'), max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = _('حجز خدمة')
        verbose_name_plural = _('حجوزات الخدمات')

    def __str__(self):
        return f"{self.service.name} - {self.booking.booking_number}"

    def save(self, *args, **kwargs):
        if not self.price_at_booking:
            self.price_at_booking = self.service.price * self.quantity
        super().save(*args, **kwargs)


class Payment(models.Model):
    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name='payment',
        verbose_name=_('الحجز')
    )
    amount = models.DecimalField(_('المبلغ'), max_digits=12, decimal_places=2)
    method = models.CharField(_('طريقة الدفع'), max_length=20, choices=PaymentMethod.choices)
    status = models.CharField(_('الحالة'), max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    
    transaction_id = models.CharField(_('رقم العملية'), max_length=100, blank=True)
    paid_at = models.DateTimeField(_('تاريخ الدفع'), null=True, blank=True)
    
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), default=timezone.now)

    class Meta:
        verbose_name = _('دفع')
        verbose_name_plural = _('المدفوعات')

    def __str__(self):
        return f"{self.booking.booking_number} - {self.get_status_display()}"

    def save(self, *args, **kwargs):
        if self.status == PaymentStatus.COMPLETED and not self.paid_at:
            self.paid_at = timezone.now()
        super().save(*args, **kwargs)


class RoomAvailability(models.Model):
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='availability',
        verbose_name=_('الغرفة')
    )
    date = models.DateField(_('التاريخ'))
    available_count = models.PositiveIntegerField(_('العدد المتاح'))
    price_override = models.DecimalField(_('سعر مخصص'), max_digits=10, decimal_places=2, null=True, blank=True)
    
    class Meta:
        verbose_name = _('توافر الغرفة')
        verbose_name_plural = _('توافر الغرف')
        unique_together = ('room', 'date')
        ordering = ['date']

    def __str__(self):
        return f"{self.room.name} - {self.date}"


class Review(models.Model): 
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name=_('الغرفة')
    )
    booking = models.OneToOneField(
        Booking,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='review',
        verbose_name=_('الحجز')
    )
    
    name = models.CharField(_('الاسم'), max_length=100)
    email = models.EmailField(_('البريد الإلكتروني'))
    rating = models.PositiveSmallIntegerField(
        _('التقييم'),
        validators=[MinValueValidator(1)],
        choices=[(i, i) for i in range(1, 6)],
        default=5
    )
    comment = models.TextField(_('التعليق'))
    is_approved = models.BooleanField(_('معتمد'), default=False)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), default=timezone.now)

    class Meta:
        verbose_name = _('تقييم')
        verbose_name_plural = _('التقييمات')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.rating}⭐"


class Contact(models.Model):
    name = models.CharField(_('الاسم'), max_length=100)
    email = models.EmailField(_('البريد الإلكتروني'))
    phone = models.CharField(_('رقم الهاتف'), max_length=20)
    subject = models.CharField(_('الموضوع'), max_length=100, choices=SubjectFlag.choices)
    message = models.TextField(_('الرسالة'))
    is_replied = models.BooleanField(_('تم الرد'), default=False)
    replied_at = models.DateTimeField(_('تاريخ الرد'), null=True, blank=True)
    reply_message = models.TextField(_('نص الرد'), blank=True)
    
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), default=timezone.now)

    class Meta:
        verbose_name = _('رسالة تواصل')
        verbose_name_plural = _('رسائل التواصل')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.get_subject_display()}"


class Notification(models.Model):
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('الحجز'),
        null=True,
        blank=True
    )
    recipient_email = models.EmailField(_('البريد المستلم'))
    subject = models.CharField(_('الموضوع'), max_length=200)
    message = models.TextField(_('الرسالة'))
    is_sent = models.BooleanField(_('تم الإرسال'), default=False)
    sent_at = models.DateTimeField(_('تاريخ الإرسال'), null=True, blank=True)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), default=timezone.now)

    class Meta:
        verbose_name = _('إشعار')
        verbose_name_plural = _('الإشعارات')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.subject} - {self.recipient_email}"