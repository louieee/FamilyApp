from django.db import models
from django.db.models import Count


# Create your models here.

class VotingSession(models.Model):
	family = models.ForeignKey("core.Family", on_delete=models.CASCADE, default=None, null=True)
	title = models.CharField(max_length=200)
	description = models.TextField()
	positions = models.ManyToManyField("Position", blank=True)
	date_conducted = models.DateTimeField(default=None, null=True)

	def winners(self):
		return [position.winner(self) for position in self.positions.all()]


class Position(models.Model):
	family = models.ForeignKey("core.Family", on_delete=models.CASCADE, default=None, null=True)
	title = models.CharField(max_length=100)
	description = models.TextField()

	def winner(self, session):
		return (
			Aspirant.objects.filter(position=self, session=session)
			.annotate(vote_count=Count("votes"))
			.order_by("-vote_count")
			.first()
		)


class Aspirant(models.Model):
	user = models.ForeignKey(
		"core.User", on_delete=models.CASCADE, related_name="aspirant"
	)
	position = models.ForeignKey("Position", on_delete=models.SET_NULL, null=True)
	session = models.ForeignKey("VotingSession", on_delete=models.CASCADE)
	votes = models.ManyToManyField("core.User", related_name="votes")
