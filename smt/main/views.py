from django.shortcuts import render
from .models import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime

def home_view(request):
    return render(request,"index.html")

def create_entry_view(request):

    return render(request,"create_entry.html",{
        "parties":Party.objects.all(),
        "vehicles":Vehicle.objects.all(),
        "drivers":Driver.objects.all(),
        "items":Item.objects.all()
    })

@csrf_exempt
def create_entry(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            # Parse date from DD-MM-YYYY format
            date_str = data['date']
            parsed_date = datetime.strptime(date_str, '%d-%m-%Y').date()
            
            party = Party.objects.get(id=data['party_id'])
            vehicle = Vehicle.objects.get(id=data['vehicle'])
            driver = Driver.objects.get(id=data['driver'])
            entry = Entry.objects.create(
                date=parsed_date,  # Use the parsed date
                customer_from=data['location_from'],
                customer_to=data['location_to'],
                party=party,
                vehicle=vehicle,
                driver=driver,
                total=sum(float(item['total']) for item in data['items'])
            )
            for item in data['items']:
                EntryItem.objects.create(
                    entry=entry,
                    item=Item.objects.get(id=item['id']),
                    quantity=item['quantity'],
                    total=item['total']
                )
            return JsonResponse({'success': True})
        except Exception as e:
            print(e)
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def driver_view(request):
    return render(request,"driver.html",{
        "drivers":Driver.objects.all()
    })

def vehicle_view(request):
    return render(request,"vehicle.html",{
        "vehicles":Vehicle.objects.all()
    })

def entry_view(request):
    entries = Entry.objects.all()
    parties = Party.objects.all()
    vehicles = Vehicle.objects.all()
    drivers = Driver.objects.all()
    
    if request.method == 'POST':
        data = request.POST
        print(data)

    return render(request, 'entry.html', {
        'entries': entries,
        'parties': parties,
        'vehicles': vehicles,
        'drivers': drivers
    })
