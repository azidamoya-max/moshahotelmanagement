from django.contrib import admin
from .models import * #Userprofile, Brand, Price, Brandt, Car, Tyre

# Register your models here.

admin.site.register(Userprofile)
admin.site.register(Price)
admin.site.register(Tyre)
admin.site.register(Tprice)
admin.site.register(Batterybrand)
admin.site.register(Tyrebrand)
#admin.site.register(Battery)