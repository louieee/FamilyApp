from gettext import gettext

from django.core.mail import send_mail

from FamilyBackend import settings
from core.services.email.system import render_email


def send_disowned_email(user: str, family: str, creator: str, email: str, lang="en") -> None:
	# if lang.startswith("en"):
	# 	lang = "en"

	context = {"user": user, "family": family, "creator": creator}
	message = render_email(f"email/family/disowned_email.txt", context)
	subject = gettext(f"Membership Termination")
	send_mail(
		subject,
		gettext(message),
		settings.DEFAULT_FROM_EMAIL,
		[email],
		fail_silently=True,
	)
	return


def send_invite_email(first_name: str, last_name: str, family: str, code: str, email: str):
	context = {"first_name": first_name, "last_name": last_name, "family": family, "code": code}
	message = render_email(f"email/family/invite.txt", context)
	subject = gettext(f"Family Membership Invite")
	send_mail(
		subject,
		gettext(message),
		settings.DEFAULT_FROM_EMAIL,
		[email],
		fail_silently=True,
	)
	return


def send_signup_email(first_name: str, last_name: str, code: str, email: str):
	context = {"first_name": first_name, "last_name": last_name,
	           "code": code}
	message = render_email(f"email/family/signup.txt", context)
	subject = gettext(f"Email Verification")
	send_mail(
		subject,
		gettext(message),
		settings.DEFAULT_FROM_EMAIL,
		[email],
		fail_silently=True,
	)
	return


def send_welcome_email(user: str, family: str, creator: str, email: str):
	context = {"user": user, "family": family, "creator": creator}
	message = render_email(f"email/family/welcome.txt", context)
	subject = gettext(f"Welcome to the {family} Family")
	send_mail(
		subject,
		gettext(message),
		settings.DEFAULT_FROM_EMAIL,
		[email],
		fail_silently=True,
	)
	return


