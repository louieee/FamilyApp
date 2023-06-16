from rest_framework.viewsets import ModelViewSet
from core.models import Family


class FamilyAPI(ModelViewSet):
    queryset = Family.objects.all()

