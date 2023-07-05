
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.viewsets import ModelViewSet

from core.models import Subscription, Apps
from core.serializers.subscription import SubscriptionSerializer, BuySubscriptionSerializer


class SubscriptionAPI(ModelViewSet):
	queryset = Subscription.objects.all()
	http_method_names = ("post", "get")
	serializer_class = SubscriptionSerializer

	family_query = openapi.Parameter(name="family", in_=openapi.IN_QUERY, type=openapi.TYPE_NUMBER,
	                                 description="sort by family ID")
	app_query = openapi.Parameter(name="app", in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
	                              description=f"sort by app: {', '.join(Apps.values)}")

	def get_queryset(self):
		return Subscription.objects.filter(family__in=self.request.user.families.all()).order_by("-id")

	def filter_queryset(self, queryset):
		app_query = self.request.query_params.get("app")
		family_query = self.request.query_params.get("family")
		if app_query:
			queryset = queryset.filter(app=app_query)
		if family_query:
			queryset = queryset.filter(family=family_query)
		return queryset

	@swagger_auto_schema(operation_summary="purchases a new subscription", 
	                     tags=["app subscription", ],
	                     request_body=BuySubscriptionSerializer)
	def create(self, request, *args, **kwargs):
		self.serializer_class = BuySubscriptionSerializer
		return super(SubscriptionAPI, self).create(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="retrieves a subscription",  tags=["app subscription", ], )
	def retrieve(self, request, *args, **kwargs):
		return super(SubscriptionAPI, self).retrieve(request, *args, **kwargs)

	@swagger_auto_schema(operation_summary="retrieves all subscriptions", 
	                     manual_parameters=[app_query, family_query],
	                     tags=["app subscription", ], )
	def list(self, request, *args, **kwargs):
		return super(SubscriptionAPI, self).list(request, *args, **kwargs)
