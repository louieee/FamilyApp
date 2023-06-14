from django.urls import path
from rest_framework.routers import SimpleRouter

from ..views import timetable

app_name = "time_table"
router = SimpleRouter()
router.register("", timetable.TimeTableAPI)

urlpatterns = [

]
urlpatterns.extend(router.urls)
