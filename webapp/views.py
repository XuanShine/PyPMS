import datetime
from datetime import datetime as dt

from django.http import JsonResponse
from django.shortcuts import render
from django.core import serializers

from .models import Stay

# Create your views here.

def home(request):
    return render(request, 'webapp/index.html')

def get_stays_between(request, start, end):
    query = Stay.get_stays_between(dt.strptime(start, "%Y-%m-%d"), dt.strptime(end, "%Y-%m-%d"))
    data = [{
                "id": n,
                "start": stay.check_in,
                "end": stay.check_out,
                "title" : stay.title(),
                "room" : stay.room
            }
            for n, stay in enumerate(query)]
    return JsonResponse(data, safe=False)
