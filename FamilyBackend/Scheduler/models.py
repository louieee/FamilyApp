from django.db import models

# Create your models here.

"create task"
"create a pipeline"
"create stages"
"arrange stages"
"add tasks"
"can add time to tasks"
"can allow checkins"


class Pipeline(models.Model):
	title = models.CharField()
	description = models.TextField()


class Stage(models.Model):
	title = models.CharField()
	description = models.TextField()
	level = models.PositiveSmallIntegerField()
	pipeline = models.ForeignKey("Pipeline", on_delete=models.CASCADE)


class Task(models.Model):
	title = models.CharField()
	description = models.TextField()
	stage = models.ForeignKey("Stage", on_delete=models.CASCADE)
	start_time = models.DateTimeField()
	end_time = models.DateTimeField()
	auto_move = models.BooleanField(default=False)
	done = models.BooleanField(default=False)
	notify = models.BooleanField(default=False)
	repeat = models.BooleanField(default=False)
	creator = models.ForeignKey("User.User", on_delete=models.CASCADE)
