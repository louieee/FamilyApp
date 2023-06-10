from django.contrib import admin

# Register your models here.
from User import models

admin.site.register(models.User)
admin.site.register(models.Couple)
