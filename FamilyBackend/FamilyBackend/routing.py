from django.urls import path

from core.consumers import *

websocket_urlpatterns = [
    path("ws/<token>/ballot/", BallotSocket.as_asgi()),
    path("ws/<token>/user/", UserSocket.as_asgi()),
    path("ws/<token>/family/", FamilySocket.as_asgi()),
    path("ws/<token>/timetable/", TimeTableSocket.as_asgi()),
    path("ws/<token>/scheduler/", SchedulerSocket.as_asgi()),
]
