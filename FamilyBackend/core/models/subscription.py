import uuid

from django.db import models
from django.utils import timezone

from core.services.email.subscription import subscription_expiry_reminder, subscription_expired_email, \
	send_payment_confirmation_email, send_new_subscription_email


class Apps(models.TextChoices):
	BallotApp = ("Ballot App", "Ballot App")
	SchedulerApp = ("Scheduler App", "Scheduler App")
	TimeTableApp = ("Timetable App", "Timetable App")


class Subscription(models.Model):
	txn_id = models.CharField(default=uuid.uuid4, unique=True, max_length=36, editable=False)
	family = models.ForeignKey("core.Family", on_delete=models.CASCADE)
	app = models.CharField(choices=Apps.choices, default=Apps.TimeTableApp, max_length=100)
	duration = models.PositiveSmallIntegerField(default=1, help_text="duration in month")
	start_date = models.DateField(default=None, null=True)
	expiry_date = models.DateField(default=None, null=True)
	activation_expiry = models.DateTimeField(default=None, null=True)
	price = models.FloatField(default=0)

	def expired(self):
		if self.expiry_date:
			return self.expiry_date < timezone.now().date()
		return None

	def send_expiry_reminder(self):
		days = (self.expiry_date - timezone.now()).days
		subscription_expiry_reminder(user=str(self.family.creator),
		                             txn_id=self.txn_id,
		                             app=self.app, days=days, email=self.family.creator.email)
		return

	def send_payment_email(self):
		send_new_subscription_email(user=str(self.family.creator),
		                            app=self.app, duration=self.duration,
		                            price=self.price, email=self.family.creator.email)
		return

	def send_expiry_email(self):
		subscription_expired_email(app=self.app, user=str(self.family.creator),
		                           txn_id=self.txn_id, email=self.family.creator.email)
		return

	def send_activation_email(self):
		send_payment_confirmation_email(user=str(self.family.creator),
		                                app=self.app, duration=self.duration,
		                                price=self.price, email=self.family.creator.email)
		return

