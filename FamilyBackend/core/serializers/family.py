from datetime import timedelta

from django.core.mail import EmailMessage
from django.utils import timezone
from rest_framework import serializers

from core.models import User, Family, FamilyTempData, FamilyTempDataTypes
from core.serializers.system import CustomCharField, CustomEmailField
from core.services.email.family import send_signup_email, send_welcome_email, send_invite_email


class FamilySerializer(serializers.ModelSerializer):
    class Meta:
        model = Family
        exclude = ("identifier", "creator")


class FamilySignupSerializer(serializers.ModelSerializer):
    family_name = CustomCharField(case="title")
    family_username = CustomCharField(case="lower")
    email = CustomEmailField()
    first_name = CustomCharField(case="title")
    last_name = CustomCharField(case="title")
    username = CustomCharField(case="lower")

    class Meta:
        model = User
        fields = ("family_name", "family_username", "first_name", "last_name", "email", "gender", "username")

    def validate(self, attrs):
        if User.objects.filter(email=attrs.get("email")).exists():
            raise serializers.ValidationError("A user already exists this email")
        if FamilyTempData.objects.filter(family__isnull=True, data_type=FamilyTempDataTypes.SIGNUP).filter(
                data__email=attrs.get("email")).exists():
            raise serializers.ValidationError("This email is taken already")
        if User.objects.filter(username=attrs.get("username")).exists():
            raise serializers.ValidationError("This username is already taken")
        if FamilyTempData.objects.filter(family__isnull=True, data_type=FamilyTempDataTypes.SIGNUP).filter(
                data__username=attrs.get("username")).exists():
            raise serializers.ValidationError("This username is taken already")

        if Family.objects.filter(username__iexact=attrs.get("family_username")).exists():
            raise serializers.ValidationError("A family with this username exists already.")
        if FamilyTempData.objects.filter(family__isnull=True, data_type=FamilyTempDataTypes.SIGNUP).filter(
                data__family_name=attrs.get("family_username")).exists():
            raise serializers.ValidationError("This username is taken already")
        return attrs

    def create(self, validated_data):
        temp_data = FamilyTempData.objects.create(data=validated_data, data_type=FamilyTempDataTypes.SIGNUP,
                                                  expiry_date=(timezone.now() + timedelta(hours=24)))
        send_signup_email(first_name=validated_data['first_name'], last_name=validated_data['last_name'],
                          code=temp_data.hash_code, email=validated_data['email'])
        return temp_data


class CreateFamilySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    name = CustomCharField(case="title")
    username = CustomCharField(case="lower")

    class Meta:
        model = Family
        fields = ("id", "name", "username")

    def validate(self, attrs):
        family = Family.objects.filter(username__iexact=attrs.get("username"))
        family = family.exclude(id=self.instance.id) if self.instance else family
        if family.exists():
            raise serializers.ValidationError("A family with this username exists already.")
        if self.instance and "username" in attrs:
            del attrs['username']
        return attrs

    def create(self, validated_data):
        user = self.context.get("user")
        family = Family.objects.create(**validated_data, creator=user)
        user.families.add(family)
        user.save()
        return family


class FamilyVerificationSerializer(serializers.Serializer):
    hash_code = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        temp_data = FamilyTempData.objects.filter(hash_code=attrs.pop("hash_code"))
        if not temp_data.exists():
            raise serializers.ValidationError("This link has expired, please you have to sign up again.")
        attrs = {** temp_data.first().data, "password": attrs.pop("password")}
        temp_data.delete()
        return attrs

    def create(self, validated_data):
        family = Family.objects.create(name=validated_data.pop("family_name"),
                                       username=validated_data.pop("family_username"))
        user = User.objects.create_user(**validated_data)
        user.families.add(family)
        user.save()
        family.creator = user
        family.save()
        return family


class FamilyInviteSerializer(serializers.Serializer):
    email = CustomEmailField()
    first_name = CustomCharField(case="title")
    last_name = CustomCharField(case="title")

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "gender", "role")

    def validate(self, attrs):
        family = self.context.get("family")
        attrs['family'] = family
        users = User.objects.filter(email=attrs.get("email"))
        if users.exists():
            attrs['user'] = users.first()
            return attrs
        if users.filter(families__username=family.username).exists():
            raise serializers.ValidationError("A family member with this email already exists.")
        if FamilyTempData.objects.filter(family=family, data_type=FamilyTempDataTypes.INVITE).filter(
                data__email=attrs.get("email")).exists():
            raise serializers.ValidationError("This email is taken already")
        return attrs

    def create(self, validated_data):
        family = validated_data.pop("family")
        if 'user' not in validated_data:
            temp_data = FamilyTempData.objects.create(family=family, data=validated_data,
                                                      data_type=FamilyTempDataTypes.INVITE,
                                                      expiry_date=(timezone.now() + timedelta(hours=24)))
            send_invite_email(first_name=validated_data['first_name'],
                              last_name=validated_data['last_name'],
                              family=str(family), code=temp_data.hash_code, email=validated_data['email'])
            return temp_data
        user = validated_data.pop("user")
        send_invite_email(first_name=user.first_name, last_name=user.last_name,
                          family=str(family), code=family.identifier, email=user.email)
        return user


class AcceptFamilyInviteSerializer(serializers.Serializer):
    username = CustomCharField(case="lower")
    hash_code = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        temp_data = FamilyTempData.objects.filter(hash_code=attrs.get("hash_code"))
        if not temp_data.exists():
            raise serializers.ValidationError("This link has expired, please ask to be re-invited")
        temp_data = temp_data.first().data
        attrs = {**attrs, **temp_data}
        if User.objects.filter(username=attrs.get("username")).exists():
            raise serializers.ValidationError("This username is taken")
        return attrs

    def create(self, validated_data):
        temp = FamilyTempData.objects.filter(hash_code=validated_data.pop("hash_code")).first()
        user = User.objects.create_user(**validated_data)
        user.families.add(temp.family)
        user.save()
        family = temp.family
        temp.delete()
        send_welcome_email(user=str(user), family=str(family), creator=str(family.creator),
                           email=user.email)
        return user


class AuthAcceptFamilyInviteSerializer(serializers.Serializer):
    hash_code = serializers.CharField()

    def validate(self, attrs):
        family = Family.objects.filter(identifier=attrs.pop("hash_code")).first()
        if not family:
            raise serializers.ValidationError("This link is invalid")
        attrs['family'] = family
        return attrs

    def create(self, validated_data):
        family = validated_data.pop("family")
        user = self.context.get("user")
        user.families.add(family)
        user.save()
        send_welcome_email(user=str(user), family=str(family), creator=str(family.creator),
                           email=user.email)
        return user
