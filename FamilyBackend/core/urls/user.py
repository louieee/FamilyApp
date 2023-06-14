from django.urls import path
from rest_framework.routers import SimpleRouter

from ..views import user

app_name = "user"
router = SimpleRouter()
router.register("", user.UserAPI)
urlpatterns = [

]
urlpatterns.extend(router.urls)
