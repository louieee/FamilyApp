from gettext import gettext

from django.core.mail import send_mail

from FamilyBackend import settings
from core.services.email.system import render_email


def send_disowned_email(
		name: str, code: str, email: str, user_type: str, lang="en"
) -> None:
	if lang.startswith("en"):
		lang = "en"

	context = {"name": name, "code": code, "user_type": user_type}
	message = render_email(f"users/{lang}/forgot_password.txt", context)
	subject = gettext("Forgot Your Password")
	send_mail(
		subject,
		gettext(message),
		settings.DEFAULT_FROM_EMAIL,
		[email],
		fail_silently=True,
	)
	return


def send_invite_email():
	...


def send_signup_email():
	...


def send_welcome_email():
	...
