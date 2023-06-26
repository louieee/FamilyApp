from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet

from core.utilities.api_response import SuccessResponse, FailureResponse
from core.models import Family, User
from core.serializers.family import FamilySignupSerializer, FamilySerializer, FamilyVerificationSerializer, \
	FamilyInviteSerializer, AcceptFamilyInviteSerializer, AuthAcceptFamilyInviteSerializer, CreateFamilySerializer


class FamilyAPI(ModelViewSet):
	queryset = Family.objects.all()
	serializer_class = FamilySerializer
	http_method_names = ("post", "patch", "get", "delete")

	def get_queryset(self):
		return self.request.user.families.objects.all()

	@swagger_auto_schema(operation_summary="views a user's families", security=[{}])
	def list(self, request, *args, **kwargs):
		return super(FamilyAPI, self).list(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="views a single user's family", security=[{}])
	def retrieve(self, request, *args, **kwargs):
		return super(FamilyAPI, self).retrieve(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="updates a single user's family", security=[{}])
	def partial_update(self, request, *args, **kwargs):
		return super(FamilyAPI, self).partial_update(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="deletes a single user's family", security=[{}])
	def destroy(self, request, *args, **kwargs):
		return super(FamilyAPI, self).destroy(request, *args, **kwargs)



	@swagger_auto_schema(
		request_body=openapi.Schema(
			type=openapi.TYPE_ARRAY,
			items=openapi.Schema(type=openapi.TYPE_INTEGER),
			example=[1, 2, 3],
			description="user IDs of the family members"
		),
		security=[{}],
		operation_summary="disowns family members"
	)
	@action(detail=True, methods=["post"], url_path="disown-members", url_name="disown-members")
	def disown_family_members(self, request, *args, **kwargs):
		if len(request.data) == 0:
			return FailureResponse(message="You haven't selected any family member")
		family = self.get_object()
		if family.creator != request.user:
			return FailureResponse(message="You cannot perform this action")
		for user_id in request.data:
			user = User.objects.filter(id=user_id).first()
			if user:
				user.families.remove(family)
				user.save()
		return SuccessResponse(message=f"Family member{'s' if len(request.data) > 1 else ''} disowned successfully")


	@swagger_auto_schema(request_body=CreateFamilySerializer,
	                     operation_summary="creates a new family", security=[{}],
	                     responses={200: FamilySerializer()})
	def create(self, request, *args, **kwargs):
		serializer = CreateFamilySerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		data = serializer.save()
		return SuccessResponse(message="Family created successfully", data=data)

	@swagger_auto_schema(request_body=FamilyVerificationSerializer,
	                     operation_summary="verifies a family signup",
	                     responses={201: FamilyVerificationSerializer()})
	@action(methods=["post"], detail=False, url_name="signup", url_path="signup")
	def verify_signup(self, request, *args, **kwargs):
		serializer = FamilyVerificationSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return SuccessResponse(message="Family verification is successful", status=status.HTTP_201_CREATED)

	@swagger_auto_schema(request_body=FamilyInviteSerializer,
	                     operation_summary="sends a family member invitation", security=[{}]
	                     )
	@action(methods=["post"], detail=False, url_name="invite-members", url_path="invite-members")
	def invite_users(self, request, *args, **kwargs):
		family = request.META.get("FAMILY")
		serializer = FamilyInviteSerializer(data=request.data, context={"family": family})
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return SuccessResponse(message="Family invitation has been sent successfully")

	@swagger_auto_schema(request_body=AcceptFamilyInviteSerializer,
	                     operation_summary="accepts a family member invitation",
	                     )
	@action(methods=["post"], detail=False, url_name="accept-invite", url_path="accept-invite")
	def accept_invite(self, request, *args, **kwargs):
		serializer = AcceptFamilyInviteSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return SuccessResponse(message="Signup is successful")

	@swagger_auto_schema(request_body=AcceptFamilyInviteSerializer,
	                     operation_summary="accepts a family member invitation",
	                     )
	@action(methods=["post"], detail=False, url_name="accept-invite-auth", url_path="accept-invite-auth")
	def accept_invite_auth(self, request, *args, **kwargs):
		serializer = AuthAcceptFamilyInviteSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return SuccessResponse(message="Invite accepted successfully")

	@swagger_auto_schema(
		request_body=FamilySignupSerializer,
		operation_summary="signs up a new family",
	)
	@action(methods=["post"], detail=False, url_name="signup", url_path="signup", permission_classes=[AllowAny,])
	def signup(self, request, *args, **kwargs):
		serializer = FamilySignupSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		data = FamilySerializer(serializer.save())
		return SuccessResponse(message="Please check your email", data=data)

