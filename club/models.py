
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class Club(models.Model):
    title = models.CharField(_('الاسم'), max_length=100)
    description = models.TextField(_('الوصف'))
    image = models.ImageField(_('الصورة'), upload_to='club/', null=True, blank=True, default='club/default.jpg')
    is_active = models.BooleanField(_('نشط'), default=True)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), default=timezone.now)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)

    class Meta:
        verbose_name = _('مجموعة')
        verbose_name_plural = _('المجموعات')
    def __str__(self):
        return self.title
    

class Workingoaches(models.Model):
    name = models.CharField(_('الاسم'), max_length=100)
    image = models.ImageField(_('الصورة'), upload_to='workingoaches/', null=True, blank=True, default='workingoaches/default.jpg')
    is_active = models.BooleanField(_('نشط'), default=True)
    job = models.CharField(_('الوظيفة'), max_length=100)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), default=timezone.now)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)

    class Meta:
        verbose_name = _('مدرب')
        verbose_name_plural = _('المدربين')
    def __str__(self):
        return self.name


class MembershipPlans(models.Model):
    name = models.CharField(_('الاسم'), max_length=100)
    price = models.DecimalField(_('السعر'), max_digits=10, decimal_places=2)
    is_active = models.BooleanField(_('نشط'), default=True)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), default=timezone.now)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)

    class Meta:
        verbose_name = _('عضوية')
        verbose_name_plural = _('العضويات')
    def __str__(self):
        return self.name
    
class MembershipPlanFeatures(models.Model):
    membership_plan = models.ForeignKey(MembershipPlans, on_delete=models.CASCADE, related_name='features', verbose_name=_('خصائص العضوية'))
    name = models.CharField(_('الاسم'), max_length=100)
    is_active = models.BooleanField(_('نشط'), default=True)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), default=timezone.now)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)

    class Meta:
        verbose_name = _('خصائص العضوية')
        verbose_name_plural = _('خصائص العضويات')
    def __str__(self):
        return self.name
    
class FacilityFlag(models.TextChoices):
    AVAILABLE = 'available', _('متاحة')
    NOT_AVAILABLE = 'not_available', _('غير متاحة')
    VIP = 'vip', _('VIP')
    MOST_REQUESTED = 'most_requested', _('الأكثر طلباً')

class Facility(models.Model):
    name = models.CharField(_('الاسم'), max_length=100)
    description = models.TextField(_('الوصف'))
    image = models.ImageField(_('الصورة'), upload_to='facility_types/', null=True, blank=True)
    price = models.DecimalField(_('السعر'), max_digits=10, decimal_places=2)
    flag = models.CharField(_('الحالة'), max_length=20, choices=FacilityFlag.choices, default=FacilityFlag.AVAILABLE)
    is_active = models.BooleanField(_('نشط'), default=True)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), default=timezone.now)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)

    class Meta:
        verbose_name = _('نوع المرفق')
        verbose_name_plural = _('أنواع المرافق')
    def __str__(self):
        return self.name
    
class FacilityServices(models.Model):
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, related_name='services', verbose_name=_('الخدمات'))
    name = models.CharField(_('الاسم'), max_length=100)
    is_active = models.BooleanField(_('نشط'), default=True)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), default=timezone.now)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)

    class Meta:
        verbose_name = _('خدمة المرفق')
        verbose_name_plural = _('خدمات المرافق')
    def __str__(self):
        return self.name

TIME_FLAG_CHOICES = [
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
    ('4', '4'),
    ('5', '5'),
    ('6', '6'),
]

class FacilityBooking(models.Model):
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, related_name='bookings', verbose_name=_('المرفق'))
    booking_date = models.DateTimeField(_('تاريخ الحجز'), default=timezone.now)
    booking_start_time = models.TimeField(_('وقت الحجز'))
    time_flag = models.CharField(_('مدة الحجز'), max_length=1, choices=TIME_FLAG_CHOICES, default='1')
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), default=timezone.now)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)

    class Meta:
        verbose_name = _('حجز المرفق')
        verbose_name_plural = _('حجوزات المرافق')
    def __str__(self):
        return f"{self.facility.name} - {self.booking_date.strftime('%Y-%m-%d %H:%M')}"