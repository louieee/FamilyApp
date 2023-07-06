from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.viewsets import ModelViewSet

from core.models import TimeTable, Row, Column, Item, Family
from core.serializers.timetable import TimeTableSerializer, RowSerializer, ColumnSerializer, ItemSerializer
from core.utilities.api_response import FailureResponse, SuccessResponse
from core.utilities.utils import get_family


class CanUseTimetable(BasePermission):
	message = "You don't have a license for the timetable app"

	def has_permission(self, request, view):
		family = Family.objects.get(username=request.META.get("HTTP_FAMILY"))
		return family.can_use_timetable()


class TimeTableAPI(ModelViewSet):
	queryset = TimeTable.objects.all()
	serializer_class = TimeTableSerializer
	http_method_names = ("post", "get", "patch", "delete")
	permission_classes = (IsAuthenticated, CanUseTimetable)

	def get_queryset(self):
		return TimeTable.objects.filter(family__user=self.request.user,
		                                family__username__iexact=get_family(self.request))

	def get_serializer_context(self):
		data = super(TimeTableAPI, self).get_serializer_context()
		data['user'] = self.request.user
		data['family'] = Family.objects.get(username__iexact=get_family(self.request))
		return data

	@swagger_auto_schema(operation_summary="creates a timetable", tags=['timetable', ],
	                     request_body=TimeTableSerializer)
	def create(self, request, *args, **kwargs):
		return super(TimeTableAPI, self).create(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="updates a timetable", tags=['timetable', ],
	                     request_body=TimeTableSerializer)
	def partial_update(self, request, *args, **kwargs):
		return super(TimeTableAPI, self).partial_update(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="retrieves a timetable", tags=['timetable', ],
	                     )
	def retrieve(self, request, *args, **kwargs):
		return super(TimeTableAPI, self).retrieve(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="retrieves a list of timetable", tags=['timetable', ],
	                     )
	def list(self, request, *args, **kwargs):
		return super(TimeTableAPI, self).list(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="deletes a timetable", tags=["timetable", ],
	                     )
	def destroy(self, request, *args, **kwargs):
		return super(TimeTableAPI, self).destroy(request, *args, **kwargs)

	@swagger_auto_schema(
		request_body=openapi.Schema(
			type=openapi.TYPE_ARRAY,
			items=openapi.Schema(type=openapi.TYPE_INTEGER),
			example=[1, 2, 3],
			description="IDs of the rows"
		),

		operation_summary="re-arrange rows in a timetable",
		tags=['timetable', ]

	)
	@action(detail=True, methods=["post"], url_path="rows/re-arrange", url_name="arrange-rows")
	def arrange_rows(self, request, *args, **kwargs):
		if len(request.data) == 0:
			return FailureResponse(message="There are no rows to be arranged")
		timetable = self.get_object()
		if timetable.creator != request.user:
			return FailureResponse(message="You cannot perform this action")
		Row.rearrange(request.data)
		rows = Row.objects.filter(timetable=timetable).order_by('level')
		return SuccessResponse(message=f"Rows have been rearranged successfully",
		                       data=RowSerializer(rows, many=True).data)

	@swagger_auto_schema(
		request_body=openapi.Schema(
			type=openapi.TYPE_ARRAY,
			items=openapi.Schema(type=openapi.TYPE_INTEGER),
			example=[1, 2, 3],
			description="IDs of the columns"
		),

		operation_summary="re-arrange columns in a timetable",
		tags=['timetable', ]

	)
	@action(detail=True, methods=["post"], url_path="columns/re-arrange", url_name="arrange-columns")
	def arrange_columns(self, request, *args, **kwargs):
		if len(request.data) == 0:
			return FailureResponse(message="There are no columns to be arranged")
		timetable = self.get_object()
		if timetable.creator != request.user:
			return FailureResponse(message="You cannot perform this action")
		Column.rearrange(request.data)
		columns = Column.objects.filter(timetable=timetable).order_by('level')
		return SuccessResponse(message=f"Columns have been rearranged successfully",
		                       data=ColumnSerializer(columns, many=True).data)


timetable_query = openapi.Parameter("timetable", in_=openapi.IN_QUERY, description="timetable ID",
                                    type=openapi.TYPE_NUMBER, required=True)


class RowAPI(ModelViewSet):
	queryset = Row.objects.order_by("level")
	serializer_class = RowSerializer
	http_method_names = ("post", "get", "patch", "delete")
	permission_classes = (IsAuthenticated, CanUseTimetable)

	def get_queryset(self):
		timetable = self.request.query_params.get("timetable")
		if timetable:
			return self.queryset.filter(timetable_id=timetable)
		return self.queryset

	@swagger_auto_schema(operation_summary="creates a row", tags=['timetable', ],
	                     request_body=RowSerializer)
	def create(self, request, *args, **kwargs):
		return super(RowAPI, self).create(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="updates a row", tags=['timetable', ],
	                     request_body=RowSerializer)
	def partial_update(self, request, *args, **kwargs):
		return super(RowAPI, self).partial_update(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="retrieves a row", tags=['timetable', ],
	                     )
	def retrieve(self, request, *args, **kwargs):
		return super(RowAPI, self).retrieve(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="retrieves a list of rows", tags=['timetable', ],
	                     manual_parameters=[timetable_query, ]
	                     )
	def list(self, request, *args, **kwargs):
		return super(RowAPI, self).list(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="deletes a row", tags=["timetable", ],
	                     )
	def destroy(self, request, *args, **kwargs):
		self.get_object().disconnect()
		return super(RowAPI, self).destroy(request, *args, **kwargs)


class ColumnAPI(ModelViewSet):
	queryset = Column.objects.order_by("level")
	http_method_names = ("post", "get", "patch", "delete")
	serializer_class = ColumnSerializer
	permission_classes = (IsAuthenticated, CanUseTimetable)

	def get_queryset(self):
		timetable = self.request.query_params.get("timetable")
		if timetable:
			return self.queryset.filter(timetable_id=timetable)
		return self.queryset

	@swagger_auto_schema(operation_summary="creates a column", tags=['timetable', ],
	                     request_body=ColumnSerializer)
	def create(self, request, *args, **kwargs):
		return super(ColumnAPI, self).create(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="updates a column", tags=['timetable', ],
	                     request_body=ColumnSerializer)
	def partial_update(self, request, *args, **kwargs):
		return super(ColumnAPI, self).partial_update(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="retrieves a column", tags=['timetable', ],
	                     )
	def retrieve(self, request, *args, **kwargs):
		return super(ColumnAPI, self).retrieve(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="retrieves a list of columns", tags=['timetable', ],
	                     manual_parameters=[timetable_query, ]
	                     )
	def list(self, request, *args, **kwargs):
		return super(ColumnAPI, self).list(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="deletes a column", tags=["timetable", ],
	                     )
	def destroy(self, request, *args, **kwargs):
		self.get_object().disconnect()
		return super(ColumnAPI, self).destroy(request, *args, **kwargs)


class ItemAPI(ModelViewSet):
	queryset = Item.objects.all()
	http_method_names = ("post", "get", "patch", "delete")
	serializer_class = ItemSerializer
	permission_classes = (IsAuthenticated, CanUseTimetable)

	row_query = openapi.Parameter("row", in_=openapi.IN_QUERY, description="row ID",
	                              type=openapi.TYPE_NUMBER, required=True)

	def get_queryset(self):
		row = self.request.query_params.get("row")
		if row:
			return self.queryset.filter(row_id=row)
		return self.queryset

	@swagger_auto_schema(operation_summary="create an item", tags=['timetable', ],
	                     request_body=ItemSerializer)
	def create(self, request, *args, **kwargs):
		return super(ItemAPI, self).create(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="updates an item", tags=['timetable', ],
	                     request_body=ItemSerializer)
	def partial_update(self, request, *args, **kwargs):
		return super(ItemAPI, self).partial_update(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="retrieves an item", tags=['timetable', ],
	                     )
	def retrieve(self, request, *args, **kwargs):
		return super(ItemAPI, self).retrieve(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="retrieves a list of items", tags=['timetable', ],
	                     manual_parameters=[row_query, ]
	                     )
	def list(self, request, *args, **kwargs):
		return super(ItemAPI, self).list(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="deletes an item", tags=["timetable", ],
	                     )
	def destroy(self, request, *args, **kwargs):
		return super(ItemAPI, self).destroy(request, *args, **kwargs)
