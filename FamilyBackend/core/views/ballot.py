from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from core.models import VotingSession, Position, Aspirant
from core.serializers.ballot import VotingSessionSerializer, CreateVotingSessionSerializer, PositionSerializer, \
    CreateAspirantSerializer, AspirantSerializer
from core.utilities.api_response import SuccessResponse


class VotingSessionAPI(ModelViewSet):
    queryset = VotingSession.objects.all()
    serializer_class = VotingSessionSerializer
    http_method_names = ("get", "post", "patch", "delete")

    @swagger_auto_schema(request_body=CreateVotingSessionSerializer,
                         operation_summary="creates a voting session",tags=['ballot',]
                         )
    def create(self, request, *args, **kwargs):
        self.serializer_class = CreateVotingSessionSerializer
        return super(VotingSessionAPI, self).create(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="retrieves a voting session",tags=['ballot',]
                         )
    def retrieve(self, request, *args, **kwargs):
        return super(VotingSessionAPI, self).retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="retrieves a list of voting sessions",tags=['ballot',]
                         )
    def list(self, request, *args, **kwargs):
        return super(VotingSessionAPI, self).list(request, *args, **kwargs)

    @swagger_auto_schema(request_body=CreateVotingSessionSerializer,
                         operation_summary="updates a voting session",tags=['ballot',]
                         )
    def partial_update(self, request, *args, **kwargs):
        self.serializer_class = CreateVotingSessionSerializer
        return super(VotingSessionAPI, self).partial_update(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="deletes a voting session", tags=['ballot',]
                         )
    def destroy(self, request, *args, **kwargs):
        return super(VotingSessionAPI, self).destroy(request, *args, **kwargs)

    @swagger_auto_schema(request_body=CreateAspirantSerializer,
                         operation_summary="creates an aspirant", tags=['ballot',]
                         )
    @action(methods=["post", ], detail=True, url_path="positions/<int:position_id>/aspirants", url_name="add-aspirant")
    def add_aspirant(self, request, *args, **kwargs):
        position = Position.objects.get(id=kwargs.get("position_id"))
        serializer = CreateAspirantSerializer(data=request.data, context={"session": self.get_object(),
                                                                          "position": position})
        serializer.is_valid(raise_exception=True)
        aspirant = serializer.save()
        return SuccessResponse(message="Aspirant has been added", data=AspirantSerializer(aspirant).data)

    @swagger_auto_schema(operation_summary="views all aspirants in this voting session" , tags=['ballot',])
    @action(methods=["get", ], detail=True, url_path="positions/<int:position_id>/aspirants", url_name="view-aspirant")
    def view_aspirants(self, requests, *args, **kwargs):
        aspirants = Aspirant.objects.filter(session=self.get_object())
        position = Position.objects.get(id=kwargs.get("position_id"))
        aspirants = aspirants.filter(position=position)
        data = AspirantSerializer(aspirants, many=True).data
        return SuccessResponse(data=data)

    @swagger_auto_schema(operation_summary="removes an aspirants from a voting session", tags=['ballot',]
                         )
    @action(methods=["delete", ], detail=False,
            url_path="aspirants/<int:aspirant_id>",
            url_name="delete-aspirant")
    def remove_aspirant(self, request, *args, **kwargs):
        aspirant = Aspirant.objects.get(id=kwargs.get("aspirant_id"))
        aspirant.delete()
        return SuccessResponse(message="Aspirant removed successfully")

    @swagger_auto_schema(operation_summary="views an aspirants in a voting session", tags=['ballot',])
    @action(methods=["get", ], detail=False,
            url_path="aspirants/<int:aspirant_id>",
            url_name="view-aspirant")
    def view_aspirant(self, request, *args, **kwargs):
        aspirant = Aspirant.objects.get(id=kwargs.get("aspirant_id"))
        data = AspirantSerializer(aspirant).data
        return SuccessResponse(message="Aspirant retrieved successfully", data=data)

    @swagger_auto_schema(operation_summary="votes for an aspirant", tags=['ballot',])
    @action(methods=["post", ], detail=False,
            url_path="aspirants/<int:aspirant_id>/vote",
            url_name="vote-aspirant")
    def vote(self, request, *args, **kwargs):
        aspirant = Aspirant.objects.get(id=kwargs.get("aspirant_id"))
        aspirant.votes.add(request.user)
        aspirant.save()
        data = AspirantSerializer(aspirant).data
        return SuccessResponse(message="Voted successfully", data=data)


class PositionAPI(ModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    http_method_names = ("get", "post", "patch", "delete")

    search_query = openapi.Parameter(name="search", in_=openapi.IN_QUERY, description="search position",
                                     type=openapi.TYPE_STRING)

    def filter_queryset(self, queryset):
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(title__icontains=search)
        return queryset

    @swagger_auto_schema(request_body=PositionSerializer,
                         operation_summary="creates a position", tags=['ballot',]
                         )
    def create(self, request, *args, **kwargs):
        return super(PositionAPI, self).create(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="retrieves a position", tags=['ballot',]
                         )
    def retrieve(self, request, *args, **kwargs):
        return super(PositionAPI, self).retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="retrieves a list of positions", tags=['ballot',],
                         manual_parameters=[search_query, ]
                         )
    def list(self, request, *args, **kwargs):
        return super(PositionAPI, self).list(request, *args, **kwargs)

    @swagger_auto_schema(request_body=PositionSerializer,
                         operation_summary="updates a position", tags=['ballot',]
                         )
    def partial_update(self, request, *args, **kwargs):
        return super(PositionAPI, self).partial_update(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="deletes a position",
                         )
    def destroy(self, request, *args, **kwargs):
        return super(PositionAPI, self).destroy(request, *args, **kwargs)
