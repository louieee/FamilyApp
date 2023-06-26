from rest_framework.viewsets import ModelViewSet
from core.models import VotingSession


"""
Todos

endpoint to create the voting session
endpoint to update voting session (endpoint to add positions to a voting)
endpoint to list positions
endpoint to search positions
endpoint to create position
endpoint to update position
endpoint to delete position
endpoint to create aspirants
endpoint to update aspirants
endpoint to delete aspirants
endpoint to vote
endpoint to view vote result
"""


class BallotAPI(ModelViewSet):
    queryset = VotingSession.objects.all()
