from django.db import models

# Create your models here.

"create a time table"
"create an item and allocate to particular time"
"Ability to generate random items during allocation"


class TimeTable(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    timed = models.BooleanField(default=False)
    item_pool = models.JSONField(default=list)
    creator = models.ForeignKey("core.User", on_delete=models.CASCADE)


class Label(models.Model):
    title = models.CharField(max_length=100)
    timetable = models.ForeignKey("TimeTable", on_delete=models.CASCADE)


class Item(models.Model):
    name = models.CharField(max_length=255)
    timetable = models.ForeignKey("TimeTable", on_delete=models.CASCADE)
    start_time = models.DateTimeField(default=None, null=True)
    end_time = models.DateTimeField(default=None, null=True)
    label = models.ForeignKey("Label", on_delete=models.SET_NULL, null=True)
