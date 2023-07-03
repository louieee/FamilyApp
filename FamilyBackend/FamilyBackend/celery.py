import os

from celery import Celery
from celery.schedules import crontab

from core.tasks import scheduler, timetable

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "FamilyBackend.settings")

app = Celery("FamilyBackend")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
	sender.add_periodic_task(crontab(minute="*"), scheduler.move_tasks.s(), name="move_task")
	sender.add_periodic_task(crontab(minute="*"), scheduler.notify_1_hr_before.s(), name="remind_an_hour_before")
	sender.add_periodic_task(crontab(minute="*"), scheduler.notify_30_mins_before.s(), name="remind_30_min_before")
	sender.add_periodic_task(crontab(minute="*"), scheduler.notify_15_mins_before.s(), name="remind_15_min_before")
	sender.add_periodic_task(crontab(minute="*"), scheduler.notify_5_mins_before.s(), name="remind_5_min_before")

	sender.add_periodic_task(crontab(minute="*"), timetable.daily_notify.s(), name="notify_daily")
	sender.add_periodic_task(crontab(minute="*"), timetable.monthly_notify.s(), name="notify_monthly")
	sender.add_periodic_task(crontab(minute="*"), timetable.weekly_notify.s(), name="notify_weekly")
	sender.add_periodic_task(crontab(minute="*"), timetable.yearly_notify.s(), name="notify_yearly")
	sender.add_periodic_task(crontab(minute="*"), timetable.titled_notify.s(), name="notify_titled")



@app.task(bind=True)
def debug_task(self):
	print('Request: {0!r}'.format(self.request))
