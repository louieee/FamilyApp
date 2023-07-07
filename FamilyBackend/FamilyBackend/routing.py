from django.urls import path

from core.consumers import *

websocket_urlpatterns = [
    path("ws/ballot/<family>/<token>/ballot/", BallotConsumer.as_asgi()),
    path("ws/user/<family>/<token>/", NotificationConsumer.as_asgi()),
    path("ws/family/<family>/<token>/family/", FamilyConsumer.as_asgi()),
    path("ws/scheduler/<family>/<token>/scheduler/", SchedulerConsumer.as_asgi()),
    path("ws/subscription/<family>/<token>/scheduler/", SubscriptionConsumer.as_asgi()),
]
