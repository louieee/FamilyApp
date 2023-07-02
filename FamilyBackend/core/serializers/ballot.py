from rest_framework import serializers

from core.models import VotingSession, Position, Aspirant
from core.serializers.system import CustomCharField
from core.serializers.user import UserSerializer


class AspirantSerializer(serializers.ModelSerializer):
	user = UserSerializer(read_only=True)
	position = serializers.CharField()
	votes = serializers.SerializerMethodField()

	class Meta:
		model = Aspirant
		exclude = ("session",)

	def get_votes(self, obj):
		return obj.votes.objects.count()


class PositionSerializer(serializers.ModelSerializer):
	winner = serializers.SerializerMethodField(read_only=True)

	class Meta:
		model = Position
		fields = "__all__"

	def get_winner(self, obj):
		return AspirantSerializer(obj.winner).data

	def validate(self, attrs):
		position = Position.objects.filter(family=attrs['family'], title__iexact=attrs['title'])
		position = position.exclude(id=self.instance.id) if self.instance else position
		if position.exists():
			raise serializers.ValidationError("A position with this title exists already")
		return attrs




class VotingSessionSerializer(serializers.ModelSerializer):
	positions = PositionSerializer(many=True)

	class Meta:
		model = VotingSession
		exclude = ("family",)


class CreateVotingSessionSerializer(serializers.ModelSerializer):
	title = CustomCharField(case="title")
	class Meta:
		model = VotingSession
		fields = ("title", "description", "family", "positions")

	def validate(self, attrs):
		session = VotingSession.objects.filter(family=attrs['family'], title__iexact=attrs['title'])
		session = session.exclude(id=self.instance.id) if self.instance else session
		if session.exists():
			raise serializers.ValidationError("A voting session with this title exists already")
		return attrs


class CreateAspirantSerializer(serializers.ModelSerializer):
	class Meta:
		model = Aspirant
		exclude = ("votes", "session")

	def validate(self, attrs):
		attrs['session'] = self.context.get("session")
		attrs['position'] = self.context.get("position")
		if Aspirant.objects.filter(user=attrs['user'], session=attrs['session']):
			raise serializers.ValidationError("This user is already vying for a position")
		return attrs
