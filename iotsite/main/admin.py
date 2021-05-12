from django.contrib import admin

from .models import User, Client, Device, Message

# Register your models here.

# admin.site.register(User)
admin.site.register(Client)
admin.site.register(Device)
admin.site.register(Message)