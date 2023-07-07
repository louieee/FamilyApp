from django.core.mail import send_mail
from django.utils.translation import gettext

from FamilyBackend import settings
from core.services.email.system import render_email


def send_item_email(timetable: str, row: str, start_time: str,
                    item_title: str, family: str, email: list):
	context = {"timetable": timetable, "row": row,
	           "item_title": item_title,
	           "family": family, "start_time": start_time}
	message = render_email(f"email/timetable/item_email.txt", context)
	subject = gettext(f"{timetable}: {item_title}")
	send_mail(
		subject,
		gettext(message),
		settings.DEFAULT_FROM_EMAIL,
		email,
		fail_silently=True,
	)
	return
