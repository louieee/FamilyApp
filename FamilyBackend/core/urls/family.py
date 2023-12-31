from django.urls import path
from rest_framework.routers import SimpleRouter

from ..views import family

app_name = "family"
router = SimpleRouter()
router.register("", family.FamilyAPI)
router.register("members/users", family.FamilyMembersAPI)

urlpatterns = []
urlpatterns.extend(router.urls)
