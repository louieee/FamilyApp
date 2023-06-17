from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(User)

admin.site.register(Family)

admin.site.register(Pipeline)
admin.site.register(Stage)
admin.site.register(Task)

admin.site.register(TimeTable)
admin.site.register(Label)
admin.site.register(Item)

admin.site.register(VotingSession)
admin.site.register(Position)
admin.site.register(Aspirant)
