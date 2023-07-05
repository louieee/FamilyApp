from django.db import models
from django.db.models import Count, Max
from django.utils import timezone


# Create your models here.

class VotingSession(models.Model):
	family = models.ForeignKey("core.Family", on_delete=models.CASCADE, default=None, null=True)
	title = models.CharField(max_length=200)
	description = models.TextField()
	positions = models.ManyToManyField("Position", blank=True)
	date_conducted = models.DateTimeField(default=None, null=True, blank=True)
	date_concluded = models.DateTimeField(default=None, null=True, blank=True)

	def can_vote(self):
		if not self.date_conducted:
			return False
		bool1 = self.date_conducted < timezone.now()
		bool2 = timezone.now() < self.date_concluded if self.date_concluded else True
		return bool1 and bool2


class Position(models.Model):
	family = models.ForeignKey("core.Family", on_delete=models.CASCADE, default=None, null=True)
	title = models.CharField(max_length=100)
	description = models.TextField()

	def __str__(self):
		return self.title

	def winner(self, session):
		users = Aspirant.objects.filter(position=self, session=session) \
			.annotate(vote_count=Count("votes")).order_by("-vote_count").values_list("id", "vote_count")
		ids = map(lambda x: x[0], filter(lambda x: x[1] == users[0][1], users))
		return Aspirant.objects.filter(id__in=ids)


class Aspirant(models.Model):
	user = models.ForeignKey(
		"core.User", on_delete=models.CASCADE, related_name="aspirant"
	)
	position = models.ForeignKey("Position", on_delete=models.SET_NULL, null=True)
	session = models.ForeignKey("VotingSession", on_delete=models.CASCADE)
	votes = models.ManyToManyField("core.User", related_name="votes")
