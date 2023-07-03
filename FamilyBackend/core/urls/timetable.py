from django.urls import path
from rest_framework.routers import SimpleRouter

from ..views import timetable

app_name = "time_table"
router = SimpleRouter()
router.register("", timetable.TimeTableAPI)
router.register("row", timetable.RowAPI)
router.register("column", timetable.ColumnAPI)
router.register("item", timetable.ItemAPI)

urlpatterns = []
urlpatterns.extend(router.urls)
