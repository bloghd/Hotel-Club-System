from django.shortcuts import render
from django.http import HttpResponse
from .models import Club, Workingoaches

def club(request):
    clubs = Club.objects.filter(is_active=True)[:3]
    workingoaches = Workingoaches.objects.filter(is_active=True)[:3]
    return render(request, 'club/club.html', 
                  {'clubs': clubs, 
                    'workingoaches': workingoaches,
                                               })
