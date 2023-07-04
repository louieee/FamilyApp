import uuid

from django.db import models


# Create your models here.
class FamilyTempDataTypes(models.TextChoices):
	SIGNUP = ("Sign Up", "Sign Up")
	INVITE = ("Invite", "Invite")
	RESET_PASSWORD = ("Reset Password", "Reset Password")


class Family(models.Model):
	identifier = models.CharField(unique=True, default=uuid.uuid4, max_length=36, editable=False)
	username = models.CharField(max_length=100, default=None, null=True)
	name = models.CharField(max_length=100)
	creator = models.ForeignKey("core.User", on_delete=models.CASCADE, null=True)

	class Meta:
		verbose_name_plural = "Families"

	def __str__(self):
		return f"{self.name} Family"


class FamilyTempData(models.Model):
	"""
		This data will be deleted after 24 hours
	"""
	hash_code = models.CharField(default=uuid.uuid4, max_length=36, unique=True, editable=False)
	family = models.ForeignKey("Family", on_delete=models.CASCADE, null=True, default=None)
	data = models.JSONField(default=dict)
	data_type = models.CharField(choices=FamilyTempDataTypes.choices, default=FamilyTempDataTypes.SIGNUP,
	                             max_length=30)
	expiry_date = models.DateTimeField(null=True, default=None)
