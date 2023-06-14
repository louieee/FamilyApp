from django.urls import path
from rest_framework.routers import SimpleRouter

from ..views import ballot

app_name = "ballot"
router = SimpleRouter()
router.register("", ballot.BallotAPI)

urlpatterns = []
urlpatterns.extend(router.urls)
