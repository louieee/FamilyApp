from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from core.serializers.user import UserSerializer
from core.utilities.api_response import SuccessResponse, FailureResponse
from core.models import Family, User, UserRole
from core.serializers.family import FamilySignupSerializer, FamilySerializer, FamilyVerificationSerializer, \
	FamilyInviteSerializer, AcceptFamilyInviteSerializer, AuthAcceptFamilyInviteSerializer, CreateFamilySerializer
from core.utilities.utils import get_family


class FamilyAPI(ModelViewSet):
	queryset = Family.objects.all()
	serializer_class = FamilySerializer
	http_method_names = ("post", "patch", "get", "delete")
	permission_classes = [IsAuthenticated, ]

	def get_queryset(self):
		return self.request.user.families.all()

	@swagger_auto_schema(operation_summary="views a user's families")
	def list(self, request, *args, **kwargs):
		return super(FamilyAPI, self).list(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="views a single user's family", )
	def retrieve(self, request, *args, **kwargs):
		return super(FamilyAPI, self).retrieve(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="updates a single user's family", request_body=CreateFamilySerializer)
	def partial_update(self, request, *args, **kwargs):
		self.serializer_class = CreateFamilySerializer
		return super(FamilyAPI, self).partial_update(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="deletes a single user's family", )
	def destroy(self, request, *args, **kwargs):
		return super(FamilyAPI, self).destroy(request, *args, **kwargs)

	@swagger_auto_schema(
		request_body=openapi.Schema(
			type=openapi.TYPE_ARRAY,
			items=openapi.Schema(type=openapi.TYPE_INTEGER),
			example=[1, 2, 3],
			description="user IDs of the family members"
		),
		operation_summary="disowns family members"
	)
	@action(detail=False, methods=["post"], url_path="disown-members", url_name="disown-members")
	def disown_family_members(self, request, *args, **kwargs):
		if len(request.data) == 0:
			return FailureResponse(message="You haven't selected any family member")
		family = Family.objects.get(username=get_family(self.request))
		if family.creator != request.user:
			return FailureResponse(message="You cannot perform this action")
		if request.user.id in request.data and family.creator == request.user:
			return FailureResponse(message="You cannot disown yourself")
		for user_id in request.data:
			user = User.objects.filter(id=user_id).first()
			if user:
				user.families.remove(family)
				user.save()
				UserRole.objects.filter(role__family=family, user=user).delete()
		return SuccessResponse(message=f"Family member{'s' if len(request.data) > 1 else ''} disowned successfully")

	@swagger_auto_schema(request_body=CreateFamilySerializer,
	                     operation_summary="creates a new family",
	                     responses={200: FamilySerializer()})
	def create(self, request, *args, **kwargs):
		serializer = CreateFamilySerializer(data=request.data, context={"user": request.user})
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return SuccessResponse(message="Family created successfully", data=serializer.data)

	@swagger_auto_schema(request_body=FamilyInviteSerializer,
	                     operation_summary="sends a family member invitation",
	                     )
	@action(methods=["post"], detail=False, url_name="invite-members", url_path="invite-members")
	def invite_users(self, request, *args, **kwargs):
		family = Family.objects.get(username=get_family(request))
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

	@swagger_auto_schema(request_body=AuthAcceptFamilyInviteSerializer,
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
	@action(methods=["post"], detail=False, url_name="signup", url_path="signup", permission_classes=[AllowAny, ])
	def signup(self, request, *args, **kwargs):
		serializer = FamilySignupSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return SuccessResponse(message="Please check your email")

	@swagger_auto_schema(request_body=FamilyVerificationSerializer,
	                     operation_summary="verifies a family signup",
	                     responses={201: FamilyVerificationSerializer()})
	@action(methods=["post"], detail=False, url_name="verify-signup", url_path="verify-signup",
	        permission_classes=[AllowAny, ])
	def verify_signup(self, request, *args, **kwargs):
		serializer = FamilyVerificationSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return SuccessResponse(message="Family verification is successful", status=status.HTTP_201_CREATED)


class FamilyMembersAPI(ModelViewSet):
	queryset = User.objects.all()
	serializer_class = UserSerializer
	http_method_names = ("get",)

	def get_queryset(self):
		family = get_family(self.request)
		return User.objects.filter(families__username=family, families__user=self.request.user).exclude(id=self.request.user.id)

	def get_serializer_context(self):
		data = super(FamilyMembersAPI, self).get_serializer_context()
		data['family'] = Family.objects.get(username=get_family(self.request))
		return data

	@swagger_auto_schema(operation_summary="retrieves a family member detail")
	def retrieve(self, request, *args, **kwargs):
		return super(FamilyMembersAPI, self).retrieve(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="retrieves a list of family members")
	def list(self, request, *args, **kwargs):
		return super(FamilyMembersAPI, self).list(request, *args, **kwargs)

