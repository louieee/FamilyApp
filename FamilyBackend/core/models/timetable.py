from django.db import models

# Create your models here.

"create a time table"
"create an item and allocate to particular time"
"Ability to generate random items during allocation"


class RowTypes(models.TextChoices):
	DAY = ("Day", "Day")
	WEEK = ("Week", "Week")
	MONTH = ("Month", "Month")
	YEAR = ("Year", "Year")
	NON_TIMED = ("Not Timed", "Not Timed")


class TimeTable(models.Model):
	family = models.ForeignKey("core.Family", on_delete=models.CASCADE, null=True)
	title = models.CharField(max_length=255)
	description = models.TextField()
	item_pool = models.JSONField(default=list)
	row_type = models.CharField(choices=RowTypes.choices, default=RowTypes.NON_TIMED, max_length=10)
	timed_column = models.BooleanField(default=False)
	creator = models.ForeignKey("core.User", on_delete=models.CASCADE)


class Row(models.Model):
	title = models.CharField(max_length=100)
	timetable = models.ForeignKey("TimeTable", on_delete=models.CASCADE)

	def items(self):
		return Item.objects.filter(row=self)


class Column(models.Model):
	title = models.CharField(max_length=100)
	start_time = models.DateTimeField(default=None, null=True)
	end_time = models.DateTimeField(default=None, null=True)
	timetable = models.ForeignKey("TimeTable", on_delete=models.CASCADE)

class Item(models.Model):
	name = models.CharField(max_length=255)
	row = models.ForeignKey("core.Row", on_delete=models.CASCADE, null=True)
	column = models.ForeignKey("core.Column", on_delete=models.CASCADE, null=True)

	def notify_start(self):
		...

	def notify_end(self):
		...
