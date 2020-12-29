from django.contrib import admin
from .models import ViberUser, Order, Requisites, Bill

admin.site.register(ViberUser)
admin.site.register(Order)
admin.site.register(Requisites)
admin.site.register(Bill)
