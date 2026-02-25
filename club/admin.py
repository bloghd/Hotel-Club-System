from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Club, Workingoaches, MembershipPlans, MembershipPlanFeatures


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

class MembershipPlanFeaturesInline(admin.TabularInline):
    model = MembershipPlanFeatures
    extra = 1

@admin.register(MembershipPlans)
class MembershipPlansAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    inlines = [MembershipPlanFeaturesInline]


@admin.register(MembershipPlanFeatures)
class MembershipPlanFeaturesAdmin(admin.ModelAdmin):
    list_display = ('membership_plan', 'name', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('membership_plan', 'name')


    
    

