from django.http import JsonResponse
from rest_framework.viewsets import ModelViewSet

from core.models import TimeTable


class TimeTableAPI(ModelViewSet):
	queryset = TimeTable.objects.all()