from rest_framework.viewsets import ModelViewSet
from core.models import VotingSession


class BallotAPI(ModelViewSet):
    queryset = VotingSession.objects.all()
