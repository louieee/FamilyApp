from django.core.mail import send_mail
from django.utils.translation import gettext

from FamilyBackend import settings
from core.services.email.system import render_email


def send_new_subscription_email(user: str, app: str, duration: int, price: float, email: str):
	context = {"user": user, "app": app, "duration": duration, "price": price}
	message = render_email(f"email/subscription/new_subscription.txt", context)
	subject = gettext(f"{app} Subscription")
	send_mail(
		subject,
		gettext(message),
		settings.DEFAULT_FROM_EMAIL,
		[email],
		fail_silently=True,
	)
	return


def send_payment_confirmation_email(user: str, app: str, duration: int, price: float, email: str):
	context = {"user": user, "app": app, "duration": duration, "price": price}
	message = render_email(f"email/subscription/payment_confirmation.txt", context)
	subject = gettext(f"{app} Subscription Payment Confirmed")
	send_mail(
		subject,
		gettext(message),
		settings.DEFAULT_FROM_EMAIL,
		[email],
		fail_silently=True,
	)
	return


def subscription_expiry_reminder(user: str, app: str, txn_id: str, days: int, email: str):
	context = {"user": user, "app": app, "txn_id": txn_id, "days": days}
	message = render_email(f"email/subscription/expiry_reminder.txt", context)
	subject = gettext(f"{app} Subscription Expiry Reminder")
	send_mail(
		subject,
		gettext(message),
		settings.DEFAULT_FROM_EMAIL,
		[email],
		fail_silently=True,
	)
	return


def subscription_expired_email(user: str, app: str, txn_id: str, email: str):
	context = {"user": user, "app": app, "txn_id": txn_id}
	message = render_email(f"email/subscription/expired_email.txt", context)
	subject = gettext(f"{app} Subscription Expired")
	send_mail(
		subject,
		gettext(message),
		settings.DEFAULT_FROM_EMAIL,
		[email],
		fail_silently=True,
	)
	return
