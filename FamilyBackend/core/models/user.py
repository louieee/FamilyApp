from itertools import chain

from django.contrib.auth.models import AbstractUser
from django.core.cache import cache
from django.db import models


# Create your models here.


class Gender(models.TextChoices):
	Male = ("Male", "Male")
	Female = ("Female", "Female")


class Role(models.Model):
	family = models.ForeignKey("core.Family", on_delete=models.CASCADE, null=True)
	name = models.CharField(max_length=255, default="")
	description = models.TextField(blank=True)


class User(AbstractUser):
	families = models.ManyToManyField("core.Family", blank=True)
	gender = models.CharField(
		max_length=10, choices=Gender.choices, default=None, null=True
	)

	def get_role(self, family):
		return UserRole.objects.filter(family=family, user=self).first()


class UserRole(models.Model):
	user = models.ForeignKey("core.User", on_delete=models.CASCADE)
	role = models.ForeignKey("core.Role", on_delete=models.CASCADE)
