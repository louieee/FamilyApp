import uuid

from django.db import models


class Apps(models.TextChoices):
	BallotApp = ("Ballot App", "Ballot App")
	SchedulerApp = ("Scheduler App", "Scheduler App")
	TimeTableApp = ("Timetable App", "Timetable App")


class Subscription(models.Model):
	txn_id = models.CharField(default=uuid.uuid4, unique=True, max_length=36, editable=False)
	family = models.ForeignKey("core.Family", on_delete=models.CASCADE)
	app = models.CharField(choices=Apps.choices, default=Apps.TimeTableApp, max_length=100)
	duration = models.PositiveSmallIntegerField(default=1)
	start_date = models.DateField()
	expiry_date = models.DateField(default=None, null=True)