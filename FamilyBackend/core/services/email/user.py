from django.core.mail import send_mail
from django.utils.translation import gettext

from FamilyBackend import settings
from core.services.email.system import render_email


def send_forgot_password_email(user: str, code: str, email: str):
	context = {"user": user, "code": code}
	message = render_email(f"email/user/forgot_password.txt", context)
	subject = gettext("Password Reset")
	send_mail(
		subject,
		gettext(message),
		settings.DEFAULT_FROM_EMAIL,
		[email],
		fail_silently=True,
	)
	return
