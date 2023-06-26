from datetime import timedelta

from django.core.mail import EmailMessage
from django.utils import timezone
from rest_framework import serializers

from core.models import Role, User, FamilyTempData, FamilyTempDataTypes
from core.serializers.system import CustomCharField, CustomEmailField
from core.serializers.family import FamilySerializer
from core.utilities.utils import get_access_token


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


class UserSerializer(serializers.ModelSerializer):
	role = serializers.SerializerMethodField(read_only=True)

	class Meta:
		model = User
		fields = ("id", "username", "email", "first_name", "last_name", "gender", "role")
		read_only_fields = ('id', "email", "role")

	def get_role(self, obj):
		family = self.context.get("family")
		if not family:
			return None
		role = obj.get_role(family)
		if not role:
			return None
		return RoleSerializer(role.role).data


class LoginSerializer(serializers.Serializer):
	email = CustomEmailField(required=False)
	username = CustomCharField(case="lower", required=False)
	password = serializers.CharField()

	def validate(self, attrs):
		if "email" in attrs:
			user = User.objects.filter(email=attrs.get('email')).first()
		elif "username" in attrs:
			user = User.objects.filter(username=attrs.get("username")).first()
		else:
			raise serializers.ValidationError("Email or Username is required")
		if not user:
			raise serializers.ValidationError("You dont have account here")
		if not user.check_password(attrs.get("password")):
			raise serializers.ValidationError("Incorrect credentials")
		return dict(user=user)

	def create(self, validated_data):
		from rest_framework_simplejwt.tokens import RefreshToken
		refresh_token = RefreshToken.for_user(user=validated_data['user'])
		validated_data['access_token'] = get_access_token(refresh_token)
		return validated_data

	def update(self, instance, validated_data):
		...


class ForgotPasswordSerializer(serializers.Serializer):
	email = CustomEmailField()

	def create(self, attrs):
		user = User.objects.filter(email=attrs.get("email")).first()
		if not user:
			return
		temp = FamilyTempData.objects.create(data=dict(email=user.email), data_type=FamilyTempDataTypes.RESET_PASSWORD,
		                                     expiry_date=(timezone.now() + timedelta(hours=24)))
		EmailMessage(subject="Reset Password Request", body=temp.hash_code, from_email="local@host.com",
		             to=[user.email, ])
		return

	def update(self, instance, validated_data):
		...


class ResetPasswordSerializer(serializers.Serializer):
	new_password = serializers.CharField()

	def create(self, validated_data):
		hash_code = self.context.get("hash_code")
		temp_data = FamilyTempData.objects.filter(hash_code=hash_code).first()
		user = User.objects.filter(email=temp_data.data['email']).first()
		if not user:
			raise serializers.ValidationError("No user with this email exists")
		user.set_password(validated_data.pop("new_password"))
		user.save()
		return user

	def update(self, instance, validated_data):
		...


class ChangePasswordSerializer(serializers.Serializer):
	old_password = serializers.CharField()
	new_password = serializers.CharField()

	def validate(self, attrs):
		user = self.context.get("user")
		if not user.check_password(attrs.pop("old_password")):
			raise serializers.ValidationError("Your password is incorrect")
		return attrs

	def create(self, validated_data):
		user = self.context.get("user")
		user.set_password(validated_data.pop("new_password"))
		user.save()
		return user

	def update(self, instance, validated_data):
		...
