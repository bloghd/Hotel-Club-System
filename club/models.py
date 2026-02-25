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

    def __str__(self):
        return self.title
    

class Workingoaches(models.Model):
    name = models.CharField(_('الاسم'), max_length=100)
    image = models.ImageField(_('الصورة'), upload_to='workingoaches/', null=True, blank=True, default='workingoaches/default.jpg')
    is_active = models.BooleanField(_('نشط'), default=True)
    job = models.CharField(_('الوظيفة'), max_length=100)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), default=timezone.now)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)

    def __str__(self):
        return self.name