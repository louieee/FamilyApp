from django.core.mail import EmailMessage
from rest_framework import serializers

from core.models import User, Family, FamilyTempData, FamilyTempDataTypes
from core.serializers.system import CustomCharField, CustomEmailField


class FamilySerializer(serializers.ModelSerializer):
	class Meta:
		model = Family
		fields = "__all__"


class FamilySignupSerializer(serializers.ModelSerializer):
	family_name = CustomCharField(case="title")
	family_username = CustomCharField(case="lower")
	email = CustomEmailField()
	first_name = CustomCharField(case="title")
	username = CustomCharField(case="lower")

	class Meta:
		model = User
		fields = ("first_name", "email", "family", "gender", "username")

	def validate(self, attrs):
		if Family.objects.filter(username__iexact=attrs.get("family_username")).exists():
			raise serializers.ValidationError("A family with this username exists already.")
		if FamilyTempData.objects.filter(family__isnull=True, data_type=FamilyTempDataTypes.SIGNUP).filter(
				data__family_name=attrs.get("family_username")).exists():
			raise serializers.ValidationError("This username is taken already")
		return attrs

	def create(self, validated_data):
		temp_data = FamilyTempData.objects.create(data=validated_data, data_type=FamilyTempDataTypes.SIGNUP)
		# TODO  more context will be added to this email section
		EmailMessage(subject="Email Verification", body=temp_data.hash_code, from_email="info@localhost",
		             to=[validated_data.get("email"), ], )
		return temp_data


class FamilyVerificationSerializer(serializers.Serializer):
	hash_code = serializers.CharField()
	password = serializers.CharField()

	def validate(self, attrs):
		temp_data = FamilyTempData.objects.filter(hash_code=attrs.pop("hash_code"))
		if temp_data:
			raise serializers.ValidationError("This link has expired, please you have to sign up again.")
		attrs = temp_data.first().data
		return attrs

	def create(self, validated_data):
		family = Family.objects.create(name=validated_data.pop("family_name"),
		                               username=validated_data.pop("family_username"))
		User.objects.create_user(**validated_data, family=family,
		                         creator=True)
		return family


class FamilyInviteSerializer(serializers.Serializer):
	email = CustomEmailField()
	first_name = CustomCharField(case="title")
	username = CustomCharField(case="lower")

	class Meta:
		model = User
		fields = ("first_name", "email", "gender", "username", "role")

	def validate(self, attrs):
		family = self.context.get("family")
		if User.objects.filter(family=family, username=attrs.get("username")).exists():
			raise serializers.ValidationError("A family member with this username already exists.")
		if User.objects.filter(family=family, email=attrs.get("email")).exists():
			raise serializers.ValidationError("A family member with this email already exists.")
		if FamilyTempData.objects.filter(family__isnull=family, data_type=FamilyTempDataTypes.INVITE).filter(
				data__username=attrs.get("username")).exists():
			raise serializers.ValidationError("This username is taken already")
		if FamilyTempData.objects.filter(family__isnull=family, data_type=FamilyTempDataTypes.INVITE).filter(
				data__email=attrs.get("email")).exists():
			raise serializers.ValidationError("This email is taken already")
		attrs['family'] = family
		return attrs

	def create(self, validated_data):
		family = self.context.get("family")
		temp_data = FamilyTempData.objects.create(family=family, data=validated_data,
		                                          data_type=FamilyTempDataTypes.INVITE)
		# TODO  more context will be added to this email section
		EmailMessage(subject=f"{family.name} Family Membership Invitation", body=temp_data.hash_code, from_email="info@localhost",
		             to=[validated_data.get("email"), ], )
		return temp_data


class AcceptFamilyInviteSerializer(serializers.Serializer):
	hash_code = serializers.CharField()
	password = serializers.CharField()

	def validate(self, attrs):
		temp_data = FamilyTempData.objects.filter(hash_code=attrs.pop("hash_code"))
		if temp_data:
			raise serializers.ValidationError("This link has expired, please ask to be re-invited")
		attrs = temp_data.first().data
		return attrs

	def create(self, validated_data):
		user = User.objects.create_user(**validated_data)
		return user
