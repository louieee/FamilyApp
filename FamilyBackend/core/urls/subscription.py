from django.urls import path
from rest_framework.routers import SimpleRouter

from ..views import subscription

app_name = "subscription"
router = SimpleRouter()
router.register("", subscription.SubscriptionAPI, basename="subscription")

urlpatterns = []
urlpatterns.extend(router.urls)
