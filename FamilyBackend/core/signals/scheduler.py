from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver

from core.models import Stage


@receiver(post_save, sender=Stage)
def connect_stage(sender, instance, created, **kwargs):
    if created:
        instance.connect()