from django.http import JsonResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.viewsets import ModelViewSet

from core.models import TimeTable, Row, Column, Item
from core.serializers.timetable import TimeTableSerializer, RowSerializer, ColumnSerializer, ItemSerializer


class TimeTableAPI(ModelViewSet):
	queryset = TimeTable.objects.all()
	serializer_class = TimeTableSerializer
	http_method_names = ("post", "get", "patch", "delete")

	@swagger_auto_schema(operation_summary="creates a timetable", tags=['timetable', ],
	                     security=[{}], request_body=TimeTableSerializer)
	def create(self, request, *args, **kwargs):
		return super(TimeTableAPI, self).create(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="updates a timetable", tags=['timetable', ],
	                     security=[{}], request_body=TimeTableSerializer)
	def partial_update(self, request, *args, **kwargs):
		return super(TimeTableAPI, self).partial_update(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="retrieves a timetable", tags=['timetable', ],
	                     security=[{}])
	def retrieve(self, request, *args, **kwargs):
		return super(TimeTableAPI, self).retrieve(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="retrieves a list of timetable", tags=['timetable', ],
	                     security=[{}])
	def list(self, request, *args, **kwargs):
		return super(TimeTableAPI, self).list(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="deletes a timetable", tags=["timetable", ],
	                     security=[{}])
	def destroy(self, request, *args, **kwargs):
		return super(TimeTableAPI, self).destroy(request, *args, **kwargs)


timetable_query = openapi.Parameter("timetable", in_=openapi.IN_QUERY, description="timetable ID",
                                    type=openapi.TYPE_NUMBER, required=True)


class RowAPI(ModelViewSet):
	queryset = Row.objects.all()
	serializer_class = RowSerializer
	http_method_names = ("post", "get", "patch", "delete")

	def get_queryset(self):
		timetable = self.request.query_params.get("timetable")
		if timetable:
			return self.queryset.filter(timetable_id=timetable)
		return self.queryset

	@swagger_auto_schema(operation_summary="creates a row", tags=['timetable', ],
	                     security=[{}], request_body=RowSerializer)
	def create(self, request, *args, **kwargs):
		return super(RowAPI, self).create(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="updates a row", tags=['timetable', ],
	                     security=[{}], request_body=RowSerializer)
	def partial_update(self, request, *args, **kwargs):
		return super(RowAPI, self).partial_update(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="retrieves a row", tags=['timetable', ],
	                     security=[{}])
	def retrieve(self, request, *args, **kwargs):
		return super(RowAPI, self).retrieve(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="retrieves a list of rows", tags=['timetable', ],
	                     security=[{}])
	def list(self, request, *args, **kwargs):
		return super(RowAPI, self).list(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="deletes a row", tags=["timetable", ],
	                     security=[{}])
	def destroy(self, request, *args, **kwargs):
		return super(RowAPI, self).destroy(request, *args, **kwargs)


class ColumnAPI(ModelViewSet):
	queryset = Column.objects.all()
	http_method_names = ("post", "get", "patch", "delete")
	serializer_class = ColumnSerializer

	def get_queryset(self):
		timetable = self.request.query_params.get("timetable")
		if timetable:
			return self.queryset.filter(timetable_id=timetable)
		return self.queryset

	@swagger_auto_schema(operation_summary="creates a column", tags=['timetable', ],
	                     security=[{}], request_body=ColumnSerializer)
	def create(self, request, *args, **kwargs):
		return super(ColumnAPI, self).create(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="updates a column", tags=['timetable', ],
	                     security=[{}], request_body=ColumnSerializer)
	def partial_update(self, request, *args, **kwargs):
		return super(ColumnAPI, self).partial_update(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="retrieves a column", tags=['timetable', ],
	                     security=[{}])
	def retrieve(self, request, *args, **kwargs):
		return super(ColumnAPI, self).retrieve(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="retrieves a list of columns", tags=['timetable', ],
	                     security=[{}])
	def list(self, request, *args, **kwargs):
		return super(ColumnAPI, self).list(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="deletes a column", tags=["timetable", ],
	                     security=[{}])
	def destroy(self, request, *args, **kwargs):
		return super(ColumnAPI, self).destroy(request, *args, **kwargs)


class ItemAPI(ModelViewSet):
	queryset = Item.objects.all()
	http_method_names = ("post", "get", "patch", "delete")
	serializer_class = ItemSerializer

	row_query = openapi.Parameter("row", in_=openapi.IN_QUERY, description="row ID",
	                              type=openapi.TYPE_NUMBER, required=True)

	def get_queryset(self):
		row = self.request.query_params.get("row")
		if row:
			return self.queryset.filter(row_id=row)
		return self.queryset

	@swagger_auto_schema(operation_summary="create an item", tags=['timetable', ],
	                     security=[{}], request_body=ItemSerializer)
	def create(self, request, *args, **kwargs):
		return super(ItemAPI, self).create(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="updates an item", tags=['timetable', ],
	                     security=[{}], request_body=ItemSerializer)
	def partial_update(self, request, *args, **kwargs):
		return super(ItemAPI, self).partial_update(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="retrieves an item", tags=['timetable', ],
	                     security=[{}])
	def retrieve(self, request, *args, **kwargs):
		return super(ItemAPI, self).retrieve(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="retrieves a list of items", tags=['timetable', ],
	                     security=[{}])
	def list(self, request, *args, **kwargs):
		return super(ItemAPI, self).list(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="deletes an item", tags=["timetable", ],
	                     security=[{}])
	def destroy(self, request, *args, **kwargs):
		return super(ItemAPI, self).destroy(request, *args, **kwargs)
