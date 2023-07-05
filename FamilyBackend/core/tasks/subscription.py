import os

import django
from celery import shared_task
from django.utils import timezone

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
