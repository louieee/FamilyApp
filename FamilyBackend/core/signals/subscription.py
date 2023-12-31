from django.db.models.signals import post_save
from django.dispatch import receiver

from core.models import Stage, Subscription, Apps
from core.services.email.subscription import send_new_subscription_email

price_data = {Apps.TimeTableApp: 1000, Apps.BallotApp: 1500, Apps.SchedulerApp: 2000}


@receiver(post_save, sender=Subscription)
def add_price(sender, instance, created, **kwargs):
	if created:
		instance.price = instance.duration * price_data[instance.app]
		instance.save()
		instance.send_payment_email()
