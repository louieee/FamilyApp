from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.viewsets import ModelViewSet

from core.models import VotingSession, Position, Aspirant, Family, User
from core.serializers.ballot import VotingSessionSerializer, CreateVotingSessionSerializer, PositionSerializer, \
	CreateAspirantSerializer, AspirantSerializer
from core.serializers.user import UserSerializer
from core.utilities.api_response import SuccessResponse, FailureResponse
from core.utilities.utils import get_family, send_ws


class CanUseBallot(BasePermission):
	message = "You don't have a license for the ballot app"

	def has_permission(self, request, view):
		family = Family.objects.get(username=request.META.get("HTTP_FAMILY"))
		return family.can_use_ballot()


class VotingSessionAPI(ModelViewSet):
	queryset = VotingSession.objects.all()
	serializer_class = VotingSessionSerializer
	http_method_names = ("get", "post", "patch", "delete")
	permission_classes = (IsAuthenticated, CanUseBallot)

	def get_queryset(self):
		return VotingSession.objects.filter(family__user=self.request.user,
		                                    family__username__iexact=get_family(self.request))

	def get_serializer_context(self):
		data = super(VotingSessionAPI, self).get_serializer_context()
		data['family'] = Family.objects.get(username__iexact=get_family(self.request))
		return data

	@swagger_auto_schema(request_body=CreateVotingSessionSerializer,
	                     operation_summary="creates a voting session", tags=['ballot', ]
	                     )
	def create(self, request, *args, **kwargs):
		self.serializer_class = CreateVotingSessionSerializer
		return super(VotingSessionAPI, self).create(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="retrieves a voting session", tags=['ballot', ]
	                     )
	def retrieve(self, request, *args, **kwargs):
		return super(VotingSessionAPI, self).retrieve(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="retrieves a list of voting sessions", tags=['ballot', ]
	                     )
	def list(self, request, *args, **kwargs):
		return super(VotingSessionAPI, self).list(request, *args, **kwargs)

	@swagger_auto_schema(request_body=CreateVotingSessionSerializer,
	                     operation_summary="updates a voting session", tags=['ballot', ]
	                     )
	def partial_update(self, request, *args, **kwargs):
		self.serializer_class = CreateVotingSessionSerializer
		return super(VotingSessionAPI, self).partial_update(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="deletes a voting session", tags=['ballot', ]
	                     )
	def destroy(self, request, *args, **kwargs):
		return super(VotingSessionAPI, self).destroy(request, *args, **kwargs)


class AspirantAPI(ModelViewSet):
	queryset = Aspirant.objects.all()
	serializer_class = AspirantSerializer
	http_method_names = ("post", "get", "delete")
	permission_classes = (IsAuthenticated, CanUseBallot)

	position_query = openapi.Parameter("position", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
	                                   description="Position ID",
	                                   required=True)
	search_query = openapi.Parameter(name="search", in_=openapi.IN_QUERY, description="search aspirant",
	                                 type=openapi.TYPE_STRING)

	def get_queryset(self):
		return Aspirant.objects.filter(position__family__username__iexact=get_family(self.request),
		                               position__family__user=self.request.user)

	def get_serializer_context(self):
		data = super(AspirantAPI, self).get_serializer_context()
		data['family'] = Family.objects.get(username__iexact=get_family(self.request))
		return data

	def filter_queryset(self, queryset):
		position = self.request.query_params.get("position")
		search = self.request.query_params.get("search")
		if position:
			queryset = queryset.filter(position_id=position)
		if search:
			queryset = queryset.filter(Q(user__first_name__icontains=search) | Q(user__last_name__icontains=search)
			                           | Q(user__email__icontains=search))
		return queryset

	@swagger_auto_schema(operation_summary="views all aspirants in a voting session", tags=['ballot', ],
	                     manual_parameters=[search_query, position_query])
	def list(self, request, *args, **kwargs):
		return super(AspirantAPI, self).list(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="views an aspirants in a voting session", tags=['ballot', ])
	def retrieve(self, request, *args, **kwargs):
		return super(AspirantAPI, self).retrieve(request, *args, **kwargs)

	@swagger_auto_schema(request_body=CreateAspirantSerializer,
	                     operation_summary="adds an aspirant", tags=['ballot', ]
	                     )
	def create(self, request, *args, **kwargs):
		self.serializer_class = CreateAspirantSerializer
		return super(AspirantAPI, self).create(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="removes an aspirants from a voting session", tags=['ballot', ]
	                     )
	def destroy(self, request, *args, **kwargs):
		return super(AspirantAPI, self).destroy(self, request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="votes for an aspirant", tags=['ballot', ])
	@action(methods=["post", ], detail=True,
	        url_path="vote",
	        url_name="vote-aspirant")
	def vote(self, request, *args, **kwargs):
		aspirant = self.get_object()
		if not aspirant.session.can_vote():
			return FailureResponse(message="Voting session is inactive")
		if User.objects.filter(votes__user_id=request.user, aspirant__position=aspirant.position,
		                    aspirant__session=aspirant.session).exists():
			return FailureResponse(message="You have voted already")
		aspirant.votes.add(request.user)
		aspirant.save()
		data = AspirantSerializer(aspirant).data
		ws_payload = data
		ws_payload['family'] = aspirant.session.family_id
		ws_payload['sender'] = UserSerializer(request.user).data
		send_ws(action="vote", family=aspirant.session.family.username,payload=ws_payload,
		        socket_type="ballot", user=request.user)
		return SuccessResponse(message="Voted successfully", data=data)


class PositionAPI(ModelViewSet):
	queryset = Position.objects.all()
	serializer_class = PositionSerializer
	http_method_names = ("get", "post", "patch", "delete")
	permission_classes = (IsAuthenticated, CanUseBallot)

	search_query = openapi.Parameter(name="search", in_=openapi.IN_QUERY, description="search position",
	                                 type=openapi.TYPE_STRING)
	session_query = openapi.Parameter(name="session", in_=openapi.IN_QUERY, description="session query",
	                                  type=openapi.TYPE_NUMBER)

	def get_queryset(self):
		return Position.objects.filter(family__username__iexact=get_family(self.request),
		                               family__user=self.request.user)

	def get_serializer_context(self):
		data = super(PositionAPI, self).get_serializer_context()
		data['family'] = Family.objects.get(username__iexact=get_family(self.request))
		session = self.request.query_params.get("session")
		if session:
			data['session'] = VotingSession.objects.get(id=session)
		return data

	def filter_queryset(self, queryset):
		session = self.request.query_params.get("session")
		search = self.request.query_params.get("search")
		if search:
			queryset = queryset.filter(title__icontains=search)
		if session:
			queryset = Position.objects.filter(aspirant__session_id=session).distinct()
		return queryset

	@swagger_auto_schema(request_body=PositionSerializer,
	                     operation_summary="creates a position", tags=['ballot', ]
	                     )
	def create(self, request, *args, **kwargs):
		return super(PositionAPI, self).create(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="retrieves a position", tags=['ballot', ]
	                     )
	def retrieve(self, request, *args, **kwargs):
		return super(PositionAPI, self).retrieve(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="retrieves a list of positions", tags=['ballot', ],
	                     manual_parameters=[search_query, session_query]
	                     )
	def list(self, request, *args, **kwargs):
		return super(PositionAPI, self).list(request, *args, **kwargs)

	@swagger_auto_schema(request_body=PositionSerializer,
	                     operation_summary="updates a position", tags=['ballot', ]
	                     )
	def partial_update(self, request, *args, **kwargs):
		return super(PositionAPI, self).partial_update(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="deletes a position", tags=['ballot', ]
	                     )
	def destroy(self, request, *args, **kwargs):
		return super(PositionAPI, self).destroy(request, *args, **kwargs)
