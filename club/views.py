from django.shortcuts import render
from django.http import HttpResponse
from .models import Club, Workingoaches, MembershipPlans, MembershipPlanFeatures

def club(request):
    clubs = Club.objects.filter(is_active=True)[:3]
    trainers = Workingoaches.objects.filter(is_active=True)[:3]
    membership_plans = MembershipPlans.objects.filter(is_active=True).prefetch_related('features')
    return render(request, 'club/club.html', 
                  {'clubs': clubs, 
                    'trainers': trainers,
                    'membership_plans': membership_plans
                                               })