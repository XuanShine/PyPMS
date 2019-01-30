import datetime
from datetime import datetime as dt

from django.http import JsonResponse
from django.shortcuts import render
from django.core import serializers

from .models import Stay, Reservation

# Create your views here.

def home(request):
    return render(request, 'webapp/index.html')

def get_stays_between(request, start, end):
    query = Stay.get_stays_between(dt.strptime(start, "%Y-%m-%d"), dt.strptime(end, "%Y-%m-%d"))
    data = [{
        "id": stay.id,
        "start": stay.check_in,
        "end": stay.check_out,
        "title" : stay.title(),
        "room" : stay.room
        }
            for n, stay in enumerate(query)]
    return JsonResponse(data, safe=False)

def getReservationFromStay(request, stayId):
    reservation = Reservation.objects.filter(stays__id=stayId)
    stays = reservation.first().stays.all()
    data = [serializers.serialize('json', reservation), serializers.serialize('json', stays)]
    return JsonResponse(data, safe=False)
