from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver

from core.models import Row, Column



@receiver(post_save, sender=Row)
def connect_row(sender, instance, created, **kwargs):
	if created:
		instance.connect()





@receiver(post_save, sender=Column)
def connect_column(sender, instance, created, **kwargs):
	if created:
		instance.connect()
