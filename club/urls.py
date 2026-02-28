from django.urls import path
from .views import (
    club,
)

app_name = 'club'

urlpatterns = [
    path('', club, name='club'),
]