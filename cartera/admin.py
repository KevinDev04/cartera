from django.contrib import admin
from .models import *

admin.site.register(Cliente)
admin.site.register(Fiador)
admin.site.register(Prestamo)
admin.site.register(Pago)

# Register your models here.
