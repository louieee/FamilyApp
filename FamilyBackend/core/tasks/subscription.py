import os
from datetime import timedelta

import django
from celery import shared_task
from django.utils import timezone

from core.serializers.user import UserSerializer
from core.utilities.utils import send_ws

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FamilyBackend.settings')
django.setup()
from core.models import Subscription


@shared_task
def delete_unpaid_subs():
	now = timezone.now()
	Subscription.objects.filter(start_date__isnull=True, expiry_date__isnull=True, activation_expiry__day=now.day,
	                            activation_expiry__month=now.month, activation_expiry__year=now.year,
	                            activation_expiry__hour=now.hour, activation_expiry__minute=now.minute).delete()
	return


def notify_end(now):
	subscriptions = Subscription.objects.filter(expiry_date__day=now.day, expiry_date__month=now.month,
	                                            expiry_date__year=now.year, expiry_date__hour=now.hour,
	                                            exppiry_date__minute=now.minute)
	for sub in subscriptions:
		sub.send_expiry_reminder()
	return subscriptions.count()


@shared_task
def notify_3_wks_before():
	now = timezone.now() + timedelta(days=21)
	notify_end(now)
	return


@shared_task
def notify_2_wks_before():
	now = timezone.now() + timedelta(days=14)
	notify_end(now)
	return


@shared_task
def notify_1_wk_before():
	now = timezone.now() + timedelta(days=7)
	notify_end(now)
	return


@shared_task
def notify_expiry():
	now = timezone.now()
	subscriptions = Subscription.objects.filter(expiry_date__day=now.day, expiry_date__month=now.month,
	                                            expiry_date__year=now.year, expiry_date__hour=now.hour,
	                                            exppiry_date__minute=now.minute)
	for sub in subscriptions:
		send_ws(user=sub.family.creator, family=sub.family.username,
		        socket_type="subscription", action="expired",
		        payload=dict(sender=UserSerializer(sub.family.creator).data,
		                     family=sub.family.id, subscription=sub.txn_id))
		sub.send_expiry_email()
	return subscriptions.count()
