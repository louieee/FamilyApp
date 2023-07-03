from django.urls import path
from rest_framework.routers import SimpleRouter

from ..views import scheduler

app_name = "scheduler"
router = SimpleRouter()
router.register("pipelines", scheduler.PipelineAPI)
router.register("stages", scheduler.StageAPI)
router.register("tasks", scheduler.TaskAPI)

urlpatterns = []
urlpatterns.extend(router.urls)
