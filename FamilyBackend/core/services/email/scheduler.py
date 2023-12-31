from django.core.mail import send_mail
from django.utils.translation import gettext

from FamilyBackend import settings
from core.services.email.system import render_email


def send_start_reminder_email(start_time: str, task_title: str, family:str,
                              task_description: str, email: list):
	context = {"start_time": start_time, "task_title": task_title,
	           "task_description": task_description, "family": family}
	message = render_email(f"email/scheduler/start_reminder.txt", context)
	subject = gettext(f"Task Reminder: {task_title}")
	send_mail(
		subject,
		gettext(message),
		settings.DEFAULT_FROM_EMAIL,
		email,
		fail_silently=True,
	)
	return


def send_task_email(task_title: str, task_description: str, family: str, email: list):
	context = {"family": family, "task_title": task_title,
	           "task_description": task_description}
	message = render_email(f"email/scheduler/notify.txt", context)
	subject = gettext(f"Task: {task_title}")
	send_mail(
		subject,
		gettext(message),
		settings.DEFAULT_FROM_EMAIL,
		email,
		fail_silently=True,
	)
	return


def send_end_reminder_email(end_time: str, task_title: str, family:str,
                            task_description: str, email: list):
	context = {"end_time": end_time, "task_title": task_title,
	           "task_description": task_description, "family": family}
	message = render_email(f"email/scheduler/end_reminder.txt", context)
	subject = gettext(f"Task Reminder: {task_title}")
	send_mail(
		subject,
		gettext(message),
		settings.DEFAULT_FROM_EMAIL,
		email,
		fail_silently=True,
	)
	return
