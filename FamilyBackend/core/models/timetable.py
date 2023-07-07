from django.db import models

from core.models import User
from core.services.email.timetable import send_item_email

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
	next_row = models.ForeignKey("Row", on_delete=models.SET_NULL, null=True)
	level = models.PositiveSmallIntegerField(default=None, null=True)

	def items(self):
		return Item.objects.filter(row=self)

	@staticmethod
	def rearrange(ids):
		curr = Row.objects.filter(id=ids[0]).first()
		index = 0
		while index < len(ids):
			next_row = Row.objects.filter \
				(id=ids[index + 1]).first() if index + 1 < len(
				ids) else None
			curr.next_row = next_row
			curr.level = index
			curr.save()
			curr = next_row
			index += 1

	def connect(self):
		last_row = Row.objects.filter(timetable=self.timetable). \
			order_by("level").exclude(id=self.id).last()
		if last_row:
			last_row.next_row = self
			last_row.save()
		self.level = (last_row.level + 1) if last_row else 0
		self.save()

	def disconnect(self):
		previous_row = Row.objects.filter(next_row=self).first()
		next_row = self.next_row
		if previous_row:
			previous_row.next_row = next_row
			previous_row.save()
		return


class Column(models.Model):
	title = models.CharField(max_length=100)
	start_time = models.DateTimeField(default=None, null=True)
	end_time = models.DateTimeField(default=None, null=True)
	timetable = models.ForeignKey("TimeTable", on_delete=models.CASCADE)
	next_column = models.ForeignKey("Column", on_delete=models.SET_NULL, null=True)
	level = models.PositiveSmallIntegerField(default=None, null=True)

	@staticmethod
	def rearrange(ids):
		curr = Column.objects.filter(id=ids[0]).first()
		index = 0
		while index < len(ids):
			next_column = Column.objects.filter \
				(id=ids[index + 1]).first() if index + 1 < len(
				ids) else None
			curr.next_column = next_column
			curr.level = index
			curr.save()
			curr = next_column
			index += 1
		return

	def connect(self):
		last_column = Column.objects.filter(timetable=self.timetable). \
			order_by("level").exclude(id=self.id).last()
		if last_column:
			last_column.next_row = self
			last_column.save()
		self.level = (last_column.level + 1) if last_column else 0
		self.save()

	def disconnect(self):
		previous_column = Column.objects.filter(next_column=self).first()
		next_column = self.next_column
		if previous_column:
			previous_column.next_column = next_column
			previous_column.save()
		return


class Item(models.Model):
	name = models.CharField(max_length=255)
	row = models.ForeignKey("core.Row", on_delete=models.CASCADE, null=True)
	column = models.ForeignKey("core.Column", on_delete=models.CASCADE, null=True)

	def notify(self):
		emails = User.objects.filter(families__username=self.row.timetable.family.username).values_list("email",
		                                                                                                flat=True)
		send_item_email(email=list(emails),
		                family=str(self.row.timetable.family),
		                item_title=self.name,
		                start_time=self.column.start_time.strftime("%d %B %Y at %I:%M%p"),
		                row=self.row.title)
		return
