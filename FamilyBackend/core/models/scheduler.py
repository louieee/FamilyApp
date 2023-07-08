from django.db import models
from django.utils import timezone

from core.services.email.scheduler import send_start_reminder_email, send_end_reminder_email, send_task_email


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

	@staticmethod
	def rearrange(stage_ids):
		curr = Stage.objects.filter(id=stage_ids[0]).first()
		index = 0
		while index < len(stage_ids):
			next_stage = Stage.objects.filter \
				(id=stage_ids[index + 1]).first() if index + 1 < len(
				stage_ids) else None
			curr.next_stage = next_stage
			curr.level = index
			curr.save()
			curr = next_stage
			index += 1

	def connect(self):
		last_stage = Stage.objects.filter(pipeline=self.pipeline).order_by("level").exclude(id=self.id).last()
		if last_stage:
			last_stage.next_stage = self
			last_stage.save()
		self.level = (last_stage.level + 1) if last_stage else 0
		self.save()

	def disconnect(self):
		previous_stage = Stage.objects.filter(next_stage=self).first()
		next_stage = self.next_stage
		if previous_stage:
			previous_stage.next_row = next_stage
			previous_stage.save()
		return


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

	def remind_creator(self, start=False):
		if start is True:
			send_start_reminder_email(start_time=self.start_time.strftime("%d %B %Y at %I:%M%p"),
			                          task_title=self.title, task_description=self.description,
			                          email=[self.creator.email, ], family=str(self.stage.pipeline.family))
			return
		send_end_reminder_email(end_time=self.end_time.strftime("%d %B %Y at %I:%M%p"),
		                        task_title=self.title, task_description=self.description,
		                        email=[self.creator.email, ], family=str(self.stage.pipeline.family))
		return

	def remind_assignees(self, start=False):
		if start is True:
			send_start_reminder_email(start_time=self.start_time.strftime("%d %B %Y at %I:%M%p"),
			                          task_title=self.title, task_description=self.description,
			                          email=list(self.assignees.values_list("email", flat=True)),
			                          family=str(self.stage.pipeline.family))
			return
		send_end_reminder_email(end_time=self.end_time.strftime("%d %B %Y at %I:%M%p"),
		                        task_title=self.title, task_description=self.description,
		                        email=list(self.assignees.values_list("email", flat=True)),
		                        family=str(self.stage.pipeline.family))
		return

	def notify(self):
		send_task_email(task_title=self.title, task_description=self.description,
		                family=str(self.stage.pipeline.family),
		                email=list(self.assignees.values_list("email", flat=True)))
