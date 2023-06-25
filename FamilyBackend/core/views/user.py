from django.contrib.auth import login
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from core.utilities.api_response import SuccessResponse, FailureResponse
from core.models import User, FamilyTempData, Family, UserRole
from core.serializers.user import RoleSerializer, LoginSerializer, UserSerializer, ResetPasswordSerializer, \
	ForgotPasswordSerializer

"""
TODOS: 

endpoint to change password
"""


class RoleAPI(ModelViewSet):
	queryset = User.objects.all()
	serializer_class = RoleSerializer

	@swagger_auto_schema(operation_summary="creates a new role")
	def create(self, request, *args, **kwargs):
		return self.create(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="retrieves list of roles")
	def list(self, request, *args, **kwargs):
		return self.list(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="retrieve a new role")
	def retrieve(self, request, *args, **kwargs):
		return self.list(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="destroys a new role")
	def destroy(self, request, *args, **kwargs):
		return self.destroy(request, *args, **kwargs)

	@swagger_auto_schema(
		request_body=openapi.Schema(
			type=openapi.TYPE_ARRAY,
			items=openapi.Schema(type=openapi.TYPE_INTEGER),
			example=[1, 2, 3],
		),
		operation_summary="assigns a role to a list of users"
	)
	@action(detail=True, methods=["post"], url_path="assign-users", url_name="assign-users")
	def assign_users(self, request, *args, **kwargs):
		# TODO: This will be updated a middleware
		family = request.META.get("FAMILY")
		family = Family.objects.get(username=family)
		if family.creator != request.user:
			return FailureResponse(message="You cannot perform this action")
		for user_id in request.data:
			UserRole.objects.update_or_create(user_id=user_id, defaults={"role": self.get_object()})
		return SuccessResponse(message="User roles updated successfully")


class ForgotPasswordAPI(APIView):
	http_method_names = ("post",)
	permission_classes = (AllowAny,)

	@swagger_auto_schema(operation_summary="allows a user to send a reset password email",
	                     request_body=ForgotPasswordSerializer)
	def post(self, request, *args, **kwargs):
		serializer = ForgotPasswordSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return SuccessResponse(message="Kindly check your email.")


class ResetPasswordAPI(APIView):
	http_method_names = ("post", "get")
	permission_classes = (AllowAny,)

	@staticmethod
	def verify_hash_code(hash_code):
		temp_data = FamilyTempData.objects.filter(hash_code=hash_code).first()
		return temp_data is not None

	@swagger_auto_schema(operation_summary="allows a user to verify the reset link code")
	def get(self, request, *args, **kwargs):
		if self.verify_hash_code(kwargs.get("hash_code")):
			return SuccessResponse(message="verified")
		return FailureResponse(message="This link is either invalid or has expired")

	@swagger_auto_schema(operation_summary="allows a user to reset their password",
	                     request_body=ResetPasswordSerializer)
	def post(self, request, *args, **kwargs):
		if not self.verify_hash_code(kwargs.get("hash_code")):
			return FailureResponse(message="This link is either invalid or has expired")
		serializer = ResetPasswordSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return SuccessResponse(message="Your password has been reset")


class UserAPI(APIView):
	http_method_names = ("patch", "get")
	permission_classes = (IsAuthenticated,)

	@swagger_auto_schema(operation_summary="retrieves a logged in user's details")
	def get(self, request, *args, **kwargs):
		data = UserSerializer(request.user).data
		return SuccessResponse(data=data)

	@swagger_auto_schema(operation_summary="updates a logged in user's details",
	                     request_body=UserSerializer, responses={200: UserSerializer()})
	def patch(self, request, *args, **kwargs):
		serializer = UserSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return SuccessResponse(data=serializer.data, message="Profile updated successfully")


class LoginAPI(APIView):
	http_method_names = ("post",)

	@swagger_auto_schema(
		request_body=LoginSerializer,
		operation_summary="logins in a user",
	)
	def post(self, request, *args, **kwargs):
		serializer = LoginSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		data = serializer.save()
		user = data.pop('user')
		login(request, user)
		return SuccessResponse(message="Login successful", data=data)
