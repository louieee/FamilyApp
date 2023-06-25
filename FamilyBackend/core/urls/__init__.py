from django.urls import path, include

urlpatterns = [
    path("family/", include("core.urls.family")),
    path("app/scheduler/", include("core.urls.scheduler")),
    path("app/timetable/", include("core.urls.timetable")),
    path("app/ballot/", include("core.urls.ballot")),
    path("users/", include("core.urls.user")),
    path("app/subscriptions/", include("core.urls.subscription"))
]
