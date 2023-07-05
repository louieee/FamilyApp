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
		return obj.votes.count()


class PositionSerializer(serializers.ModelSerializer):
	winners = serializers.SerializerMethodField(read_only=True)

	class Meta:
		model = Position
		fields = "__all__"
		read_only_fields = ("family",)

	def get_winners(self, obj):
		session = self.context.get("session")
		if session:
			return AspirantSerializer(obj.winner(session), many=True).data
		return None

	def validate(self, attrs):
		attrs['family'] = self.context.get("family")
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
		fields = ("title", "description", "positions", "date_conducted", 'date_concluded')

	def validate(self, attrs):
		attrs['family'] = self.context.get("family")
		if "title" in attrs:
			session = VotingSession.objects.filter(family=attrs['family'], title__iexact=attrs['title'])
			session = session.exclude(id=self.instance.id) if self.instance else session
			if session.exists():
				raise serializers.ValidationError("A voting session with this title exists already")
		return attrs


class CreateAspirantSerializer(serializers.ModelSerializer):
	class Meta:
		model = Aspirant
		exclude = ("votes",)

	def validate(self, attrs):
		if Aspirant.objects.filter(user=attrs['user'], session=attrs['session']):
			raise serializers.ValidationError("This user is already vying for a position")
		return attrs
