from django.contrib import admin

from .models import Contract, Order, MessageRecipient

# Register your models here.
admin.site.register(Contract)
admin.site.register(Order)
admin.site.register(MessageRecipient)
