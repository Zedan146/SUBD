from django.contrib import admin
from .models import Courier, Order, Client, Vehicle


admin.site.register(Courier)
admin.site.register(Order)
admin.site.register(Client)
admin.site.register(Vehicle)

