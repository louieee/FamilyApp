import os

import django
from celery import shared_task
from django.utils import timezone

from core.serializers.user import UserSerializer
from core.utilities.utils import send_ws

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FamilyBackend.settings')
django.setup()
from datetime import timedelta

from core.models import Task


@shared_task
def move_tasks():
	"""
		Will be run every minute
	:return:
	"""
	now = timezone.now()
	tasks = Task.objects.filter(done=False, end_time__day=now.day, end_time__month=now.month,
	                            end_time__year=now.year, end_time__hour=now.hour, end_time__minute=now.minute)
	for task in tasks:
		if task.stage.next_stage and task.auto_move is True:
			task.stage = tasks.stage.next_stage
			send_ws(user=task.creator, family=task.stage.pipeline.family.username,
			        action="move", socket_type="scheduler",
			        payload=dict(sender=UserSerializer(task.creator).data,
			                     family=task.stage.pipeline.family.id,
			                     task=task.title,
			                     stage=task.stage.next_stage.title))
		if (task.auto_done is True and task.auto_move is False) or (task.auto_move and not task.stage.next_stage):
			task.done = True
		task.save()
		if task.auto_move is True or task.repeat is True:
			task.update_time()
		task.remind_creator()
		task.remind_assignees()
	return tasks.count()


def notify_end(now):
	tasks = Task.objects.filter(done=False, end_time__day=now.day, end_time__month=now.month,
	                            end_time__year=now.year, end_time__hour=now.hour, end_time__minute=now.minute)
	for task in tasks:
		task.remind_assignees()
		task.remind_creator()
	return tasks.count()


def notify_start(now):
	tasks = Task.objects.filter(done=False, start_time__day=now.day, start_time__month=now.month,
	                            start_time__year=now.year, start_time__hour=now.hour,
	                            start_time__minute=now.minute)
	for task in tasks:
		task.remind_assignees(True)
		task.remind_creator(True)
	return tasks.count()


@shared_task
def notify_1_hr_before():
	now = timezone.now() + timedelta(hours=1)
	notify_end(now)
	notify_start(now)
	return


@shared_task
def notify_30_mins_before():
	now = timezone.now() + timedelta(minutes=30)
	notify_end(now)
	notify_start(now)
	return


@shared_task
def notify_15_mins_before():
	now = timezone.now() + timedelta(minutes=15)
	notify_end(now)
	notify_start(now)
	return


@shared_task
def notify_5_mins_before():
	now = timezone.now() + timedelta(minutes=5)
	notify_end(now)
	notify_start(now)
	return
