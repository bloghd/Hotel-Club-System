from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Club, Workingoaches


@admin.register(Workingoaches)
class WorkingoachesAdmin(admin.ModelAdmin):
    list_display = ('name', 'job', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'job')


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title',)


    
    

