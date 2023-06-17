from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet

from Utilities.api_response import SuccessResponse, FailureResponse
from core.models import User
from core.serializers import RoleSerializer

"""
endpoint to login a member into a family
endpoint to update a member's profile
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
		if not request.user.creator:
			return FailureResponse(message="You cannot perform this action")
		User.objects.filter(id__in=request.data).update(role=self.get_object())
		return SuccessResponse(message="User roles updated successfully")





