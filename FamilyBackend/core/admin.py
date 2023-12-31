from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(User)
admin.site.register(Role)
admin.site.register(UserRole)

admin.site.register(Family)
admin.site.register(FamilyTempData)
admin.site.register(Subscription)

admin.site.register(Pipeline)
admin.site.register(Stage)
admin.site.register(Task)

admin.site.register(TimeTable)
admin.site.register(Row)
admin.site.register(Column)
admin.site.register(Item)

admin.site.register(VotingSession)
admin.site.register(Position)
admin.site.register(Aspirant)
