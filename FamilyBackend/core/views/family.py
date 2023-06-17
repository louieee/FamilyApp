from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet

from Utilities.api_response import SuccessResponse
from core.models import Family
from core.serializers import FamilySignupSerializer, FamilySerializer, FamilyVerificationSerializer, \
	FamilyInviteSerializer, AcceptFamilyInviteSerializer


class FamilyAPI(ModelViewSet):
	queryset = Family.objects.all()

	@swagger_auto_schema(request_body=FamilySignupSerializer,
	                     operation_summary="signs up a new family",
	                     responses={200: FamilySerializer()})
	@action(methods=["post"], detail=False, url_name="signup", url_path="signup")
	def create(self, request, *args, **kwargs):
		serializer = FamilySignupSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		data = serializer.save()
		return SuccessResponse(message="Please check your email to continue", data=data)

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
	                     operation_summary="sends a family member invitation",
	                     )
	@action(methods=["post"], detail=False, url_name="invite-members", url_path="invite-members")
	def invite_users(self, request, *args, **kwargs):
		serializer = FamilyInviteSerializer(data=request.data, context={"family": request.user.family})
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return SuccessResponse(message="Family invitation has been sent successfully")

	@swagger_auto_schema(request_body=AcceptFamilyInviteSerializer,
	                     operation_summary="accepts a family member invitation",
	                     )
	@action(methods=["post"], detail=False, url_name="accept-invite", url_path="accept-invite")
	def invite_users(self, request, *args, **kwargs):
		serializer = AcceptFamilyInviteSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return SuccessResponse(message="Signup is successful")
