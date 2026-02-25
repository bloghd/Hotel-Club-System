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