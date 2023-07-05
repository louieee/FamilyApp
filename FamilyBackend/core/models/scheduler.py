from django.db import models
from django.utils import timezone


# Create your models here.


class Pipeline(models.Model):
	family = models.ForeignKey("core.Family", on_delete=models.CASCADE, null=True, default=True)
	title = models.CharField(max_length=200)
	description = models.TextField()
	creator = models.ForeignKey(
		"core.User", on_delete=models.CASCADE, related_name="pipeline_creator", default=None, null=True
	)
	date_created = models.DateTimeField(auto_now_add=True)


class Stage(models.Model):
	title = models.CharField(max_length=100)
	description = models.TextField()
	level = models.PositiveSmallIntegerField(default=0, blank=True)
	next_stage = models.ForeignKey("Stage", on_delete=models.SET_NULL, null=True, default=None)
	pipeline = models.ForeignKey("Pipeline", on_delete=models.CASCADE)


class Task(models.Model):
	title = models.CharField(max_length=200)
	description = models.TextField()
	stage = models.ForeignKey("Stage", on_delete=models.CASCADE)
	start_time = models.DateTimeField(blank=True)
	end_time = models.DateTimeField(blank=True)
	auto_move = models.BooleanField(default=False)
	auto_done = models.BooleanField(default=False)
	done = models.BooleanField(default=False)
	repeat = models.BooleanField(default=False)
	assignees = models.ManyToManyField("core.User")
	creator = models.ForeignKey(
		"core.User", on_delete=models.CASCADE, related_name="task_creator"
	)

	def update_time(self):
		duration = self.end_time - self.start_time
		self.start_time = timezone.now()
		self.end_time = timezone.now() + duration
		self.save()

	def remind_creator(self):
		...

	def remind_assignees(self):
		...

	def notify(self):
		...

