from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.viewsets import ModelViewSet

from core.models import Pipeline, Task, Stage, Family
from core.serializers.scheduler import PipelineSerializer, StageSerializer, CreateTaskSerializer, TaskSerializer, \
	UpdateStageSerializer
from core.utilities.api_response import SuccessResponse, FailureResponse
from core.utilities.utils import get_family


class CanUseScheduler(BasePermission):
	message = "You don't have a license for the scheduler app"

	def has_permission(self, request, view):
		family = Family.objects.get(username=request.META.get("HTTP_FAMILY"))
		return family.can_use_scheduler()


class PipelineAPI(ModelViewSet):
	queryset = Pipeline.objects.all()
	serializer_class = PipelineSerializer
	http_method_names = ("get", "post", "patch", "delete")
	permission_classes = (IsAuthenticated, CanUseScheduler)

	def get_serializer_context(self):
		data = super(PipelineAPI, self).get_serializer_context()
		data['user'] = self.request.user
		data['family'] = Family.objects.get(username__iexact=get_family(self.request))
		return data

	def get_queryset(self):
		return Pipeline.objects.filter(family__username__iexact=get_family(self.request))

	@swagger_auto_schema(operation_summary="create a pipeline", tags=['scheduler', ],
	                     request_body=PipelineSerializer)
	def create(self, request, *args, **kwargs):
		return super(PipelineAPI, self).create(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="updates a pipeline", tags=['scheduler', ],
	                     request_body=PipelineSerializer)
	def partial_update(self, request, *args, **kwargs):
		return super(PipelineAPI, self).partial_update(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="retrieves a pipeline", tags=['scheduler', ],
	                     )
	def retrieve(self, request, *args, **kwargs):
		return super(PipelineAPI, self).retrieve(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="retrieves a list of pipelines", tags=['scheduler', ],
	                     )
	def list(self, request, *args, **kwargs):
		return super(PipelineAPI, self).list(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="deletes a pipeline", tags=["scheduler", ],
	                     )
	def destroy(self, request, *args, **kwargs):
		self.get_object().disconnect()
		return super(PipelineAPI, self).destroy(request, *args, **kwargs)

	@swagger_auto_schema(
		request_body=openapi.Schema(
			type=openapi.TYPE_ARRAY,
			items=openapi.Schema(type=openapi.TYPE_INTEGER),
			example=[1, 2, 3],
			description="IDs of the stages"
		),

		operation_summary="re-arrange stages in a pipeline",
		tags=['scheduler', ]

	)
	@action(detail=True, methods=["post"], url_path="stages/re-arrange", url_name="arrange-stages")
	def arrange_stages(self, request, *args, **kwargs):
		if len(request.data) == 0:
			return FailureResponse(message="There are no stages to be arranged")
		pipeline = self.get_object()
		if pipeline.creator != request.user:
			return FailureResponse(message="You cannot perform this action")
		Stage.rearrange(request.data)
		stages = Stage.objects.filter(pipeline=pipeline).order_by('level')
		return SuccessResponse(message=f"stages have been rearranged successfully",
		                       data=StageSerializer(stages, many=True).data)


class StageAPI(ModelViewSet):
	queryset = Stage.objects.all()
	serializer_class = StageSerializer
	http_method_names = ("get", "post", "patch", "delete")
	permission_classes = (IsAuthenticated, CanUseScheduler)

	pipeline_query = openapi.Parameter('pipeline', in_=openapi.IN_QUERY, type=openapi.TYPE_NUMBER,
	                                   description="Pipeline ID",
	                                   required=True)

	def get_queryset(self):
		pipeline = self.request.query_params.get("pipeline")
		if pipeline:
			return self.queryset.filter(pipeline_id=pipeline, pipeline__family__username__exact=get_family(self.request)).order_by("level")
		return self.queryset

	@swagger_auto_schema(request_body=StageSerializer,
	                     operation_summary="adds a stage to a pipeline", tags=['scheduler', ])
	def create(self, request, *args, **kwargs):
		return super(StageAPI, self).create(request, *args, **kwargs)

	@swagger_auto_schema(request_body=UpdateStageSerializer,
	                     operation_summary="updates a stage in a pipeline", tags=['scheduler', ])
	def partial_update(self, request, *args, **kwargs):
		self.serializer_class = UpdateStageSerializer
		return super(StageAPI, self).partial_update(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="retrieves stages in a pipeline", tags=['scheduler', ],
	                     manual_parameters=[pipeline_query, ])
	def list(self, request, *args, **kwargs):
		return super(StageAPI, self).list(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="retrieves a stage in a pipeline", tags=['scheduler', ])
	def retrieve(self, request, *args, **kwargs):
		return super(StageAPI, self).retrieve(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="deletes a stage in a pipeline", tags=['scheduler', ])
	def destroy(self, request, *args, **kwargs):
		return super(StageAPI, self).destroy(request, *args, **kwargs)


class TaskAPI(ModelViewSet):
	queryset = Task.objects.all()
	serializer_class = TaskSerializer
	http_method_names = ("get", "post", "patch", "delete")
	permission_classes = (IsAuthenticated, CanUseScheduler)

	stage_query = openapi.Parameter('stage', in_=openapi.IN_QUERY, type=openapi.TYPE_NUMBER,
	                                description="Stage ID",
	                                required=True)

	def get_serializer_context(self):
		data = super(TaskAPI, self).get_serializer_context()
		data['user'] = self.request.user
		return data

	def get_queryset(self):
		stage = self.request.query_params.get("stage")
		self.queryset = self.queryset.filter(stage__pipeline__family=Family.objects.get(username__iexact=get_family(self.request)))
		if stage:
			self.queryset = self.queryset.filter(stage=stage)
		return self.queryset

	@swagger_auto_schema(request_body=CreateTaskSerializer,
	                     operation_summary="adds a task to a stage in a pipeline", tags=['scheduler', ])
	def create(self, request, *args, **kwargs):
		self.serializer_class = CreateTaskSerializer
		return super(TaskAPI, self).create(request, *args, **kwargs)

	@swagger_auto_schema(request_body=CreateTaskSerializer,
	                     operation_summary="updates a task in a stage", tags=['scheduler', ])
	def partial_update(self, request, *args, **kwargs):
		self.serializer_class = CreateTaskSerializer
		return super(TaskAPI, self).partial_update(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="retrieves all tasks in a stage", tags=['scheduler', ],
	                     manual_parameters=[stage_query,])
	def list(self, request, *args, **kwargs):
		return super(TaskAPI, self).list(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="retrieves a task in a stage", tags=['scheduler', ])
	def retrieve(self, request, *args, **kwargs):
		return super(TaskAPI, self).retrieve(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="deletes a task in a stage", tags=['scheduler', ])
	def destroy(self, request, *args, **kwargs):
		return super(TaskAPI, self).destroy(request, *args, **kwargs)
