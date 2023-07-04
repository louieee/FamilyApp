import os

import django
from celery import shared_task
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FamilyBackend.settings')
django.setup()
from core.models import FamilyTempData

@shared_task
def clear_expired_temp_data():
	now = timezone.now()
	FamilyTempData.objects.filter(expiry_date__day=now.day, expiry_date__month=now.month,
	                            expiry_date__year=now.year, expiry_date__hour=now.hour,
	                              expiry_date__minute=now.minute).delete()
	return
