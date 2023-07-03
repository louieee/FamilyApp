import os

import django
from celery import shared_task
from django.utils import timezone

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
		if task.auto_done:
			task.done = True
		task.save()
		if task.auto_move is True or task.repeat is True:
			task.update_time()
		task.notify()
	return tasks.count()


def notify(now):
	tasks = Task.objects.filter(done=False, end_time__day=now.day, end_time__month=now.month,
	                            end_time__year=now.year, end_time__hour=now.hour, end_time__minute=now.minute)
	for task in tasks:
		task.remind_assignees()
		task.remind_creator()
	return tasks.count()


@shared_task
def notify_1_hr_before():
	now = timezone.now() + timedelta(hours=1)
	return notify(now)


@shared_task
def notify_30_mins_before():
	now = timezone.now() + timedelta(minutes=30)
	return notify(now)


@shared_task
def notify_15_mins_before():
	now = timezone.now() + timedelta(minutes=15)
	return notify(now)


@shared_task
def notify_5_mins_before():
	now = timezone.now() + timedelta(minutes=5)
	return notify(now)
