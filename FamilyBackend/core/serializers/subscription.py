from rest_framework import serializers

from core.models import Subscription
from core.serializers.family import FamilySerializer


class SubscriptionSerializer(serializers.ModelSerializer):
	family = FamilySerializer(read_only=True)

	class Meta:
		model = Subscription
		fields = "__all__"


class BuySubscriptionSerializer(serializers.ModelSerializer):
	class Meta:
		model = Subscription
		fields = ("family", "app", "duration")
