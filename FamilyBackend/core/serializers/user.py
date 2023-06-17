from rest_framework import serializers

from core.models import Role
from core.serializers import CustomCharField


class RoleSerializer(serializers.ModelSerializer):
	name = CustomCharField(case="title", required=False)

	class Meta:
		model = Role
		exclude = ("family",)

	def validate(self, attrs):
		attrs['family'] = self.context.get("family")
		role = Role.objects.filter(name=attrs.get("name"), family=attrs.get('family'))
		role = role.exclude(id=self.instance.id) if self.instance else role
		if role.exists():
			raise serializers.ValidationError(detail="A Role with this name exists already.")
		return attrs

