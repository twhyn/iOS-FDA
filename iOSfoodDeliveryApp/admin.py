from django.contrib import admin

# Register your models here.
from iOSfoodDeliveryApp.models import Restaurant

# import restaurant to admin side, see in /admin/
admin.site.register(Restaurant)