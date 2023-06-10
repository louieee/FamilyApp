from django.db import models

# Create your models here.

"assign delegates"
"ability to vote for delegate"
"winner anounced"


class VotingSession(models.Model):
	title = models.CharField()
	description = models.CharField()


class Position(models.Model):
	title = models.CharField()
	description = models.CharField()


class Aspirant(models.Model):
	user = models.ForeignKey("User.User", on_delete=models.CASCADE)
	position = models.ForeignKey("Position", on_delete=models.SET_NULL, null=True)
	session = models.ForeignKey("VotingSession", on_delete=models.CASCADE)

	def


class Vote(models.Model):
	aspirant = models.ForeignKey("Aspirant", on_delete=models.CASCADE)
	user = models.ForeignKey("User.User", on_delete=models.CASCADE)


