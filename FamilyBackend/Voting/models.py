from django.db import models
from django.db.models import Sum, Count

# Create your models here.

"assign delegates"
"ability to vote for delegate"
"winner anounced"


class VotingSession(models.Model):
	title = models.CharField()
	description = models.TextField()
	positions = models.ManyToManyField("Position")

	def winners(self):
		return [position.winner(self) for position in self.positions.all()]


class Position(models.Model):
	title = models.CharField()
	description = models.TextField()

	def winner(self, session):
		return Aspirant.objects.filter(position=self, session=session). \
			annotate(vote_count=Count('votes')).order_by('-vote_count').first()


class Aspirant(models.Model):
	user = models.ForeignKey("User.User", on_delete=models.CASCADE)
	position = models.ForeignKey("Position", on_delete=models.SET_NULL, null=True)
	session = models.ForeignKey("VotingSession", on_delete=models.CASCADE)
	votes = models.ManyToManyField("User.User")
