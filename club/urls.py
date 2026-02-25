from django.urls import path
from .views import (
    club,
    membership_plans
)

app_name = 'club'

urlpatterns = [
    path('', club, name='club'),
    path('membership/', membership_plans, name='membership_plans'),
]