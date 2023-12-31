from django.contrib.auth import login
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from core.models import User, FamilyTempData, Family, UserRole, Role
from core.serializers.user import RoleSerializer, LoginSerializer, UserSerializer, ResetPasswordSerializer, \
	ForgotPasswordSerializer, ChangePasswordSerializer
from core.utilities.api_response import SuccessResponse, FailureResponse
from core.utilities.utils import get_family


class RoleAPI(ModelViewSet):
	queryset = Role.objects.all()
	serializer_class = RoleSerializer
	permission_classes = (IsAuthenticated, )
	http_method_names = ("post", "get", "delete")

	def get_queryset(self):
		family = get_family(self.request)
		return self.queryset.filter(family__username=family)

	def get_serializer_context(self):
		data = super(RoleAPI, self).get_serializer_context()
		data['family'] = Family.objects.get(username=get_family(self.request))
		return data

	@swagger_auto_schema(request_body=RoleSerializer, operation_summary="creates a new role")
	def create(self, request, *args, **kwargs):
		return super(RoleAPI, self).create(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="retrieves list of roles")
	def list(self, request, *args, **kwargs):
		return super(RoleAPI, self).list(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="retrieve a new role")
	def retrieve(self, request, *args, **kwargs):
		return super(RoleAPI, self).list(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="destroys a new role")
	def destroy(self, request, *args, **kwargs):
		return super(RoleAPI, self).destroy(request, *args, **kwargs)

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
		family = get_family(request)
		family = Family.objects.get(username=family)
		if family.creator_id != request.user.id:
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
		serializer = ResetPasswordSerializer(data=request.data, context={"hash_code": kwargs.get("hash_code")})
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return SuccessResponse(message="Your password has been reset")


class UserAPI(APIView):
	http_method_names = ("patch", "get")
	permission_classes = (IsAuthenticated,)



	@swagger_auto_schema(operation_summary="retrieves a logged in user's details")
	def get(self, request, *args, **kwargs):
		data = UserSerializer(request.user, context={"family": Family.objects.get(username=get_family(request))}).data
		return SuccessResponse(data=data)

	@swagger_auto_schema(operation_summary="updates a logged in user's details",
	                     request_body=UserSerializer, responses={200: UserSerializer()})
	def patch(self, request, *args, **kwargs):
		serializer = UserSerializer(data=request.data, partial=True, instance=request.user,
		                            context={"family": Family.objects.get(username=get_family(request))})
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return SuccessResponse(data=serializer.data, message="Profile updated successfully")


class LoginAPI(APIView):
	http_method_names = ("post",)
	permission_classes = [AllowAny, ]

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


class ChangePasswordAPI(APIView):
	http_method_names = ("post",)
	permission_classes = (IsAuthenticated,)

	@swagger_auto_schema(operation_summary="allows a user to change their password",
	                     request_body=ChangePasswordSerializer)
	def post(self, request, *args, **kwargs):
		serializer = ChangePasswordSerializer(data=request.data, context={"user": request.user})
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return SuccessResponse(message="Password changed successfully")
