from django.urls import path
from .views import *

urlpatterns = [
    path("",home_view,name="home"),
    path("create_entry/",create_entry_view,name="entry_create"),
    path("driver/",driver_view,name="driver"),
    path("vehicle/",vehicle_view,name="vehicle"),
    path("entry/",entry_view,name="entry"),

    path('ajax/create-entry/', create_entry, name='ajax_create_entry'),
]

