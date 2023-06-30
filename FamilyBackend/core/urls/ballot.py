from django.urls import path
from rest_framework.routers import SimpleRouter

from ..views import ballot

app_name = "ballot"
router = SimpleRouter()
router.register("", ballot.VotingSessionAPI, basename="ballot")
router.register("positions", ballot.PositionAPI, basename="positions")

urlpatterns = []
urlpatterns.extend(router.urls)
