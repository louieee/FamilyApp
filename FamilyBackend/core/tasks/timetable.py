import os

import django
from celery import shared_task
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FamilyBackend.settings')
django.setup()
from core.models import Item, RowTypes


def notify(items, now):
	start_items = items.filter(column__start_time__day=now.day, column__start_time__month=now.month,
	                           column__start_time__year=now.year, column__start_time__hour=now.hour,
	                           column__start_time__minute=now.minute)

	end_items = items.filter(column__end_time__day=now.day, column__end_time__month=now.month,
	                         column__end_time__year=now.year, column__end_time__hour=now.hour,
	                         column__end_time__minute=now.minute)
	for item in start_items:
		item.notify_start()
	for item in end_items:
		item.notify_end()
	return start_items.count() + end_items.count()


@shared_task
def daily_notify():
	now = timezone.now()
	now3 = timezone.now()
	today = now.strftime("%A")
	items = Item.objects.filter(row__timetable__row_type=RowTypes.DAY, column__timetable__timed_column=True,
	                            row__title__iexact=today)
	return notify(items, now)


@shared_task
def weekly_notify():
	now = timezone.now()
	week = f"Week {(now.day // 7) + 1}"
	items = Item.objects.filter(row__timetable__row_type=RowTypes.WEEK, column__timetable__timed_column=True,
	                            row__title__iexact=week)
	return notify(items, now)


@shared_task
def monthly_notify():
	now = timezone.now()
	month = now.strftime("%B")
	items = Item.objects.filter(row__timetable__row_type=RowTypes.MONTH, column__timetable__timed_column=True,
	                            row__title__iexact=month)
	return notify(items, now)


@shared_task
def yearly_notify():
	now = timezone.now()
	year = str(now.year)
	items = Item.objects.filter(row__timetable__row_type=RowTypes.YEAR, column__timetable__timed_column=True,
	                            row__title__iexact=year)
	return notify(items, now)


@shared_task
def titled_notify():
	now = timezone.now()
	items = Item.objects.filter(row__timetable__row_type=RowTypes.NON_TIMED, column__timetable__timed_column=True)
	return notify(items, now)
