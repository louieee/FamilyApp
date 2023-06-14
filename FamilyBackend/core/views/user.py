from rest_framework.viewsets import ModelViewSet

from core.models import User


class UserAPI(ModelViewSet):
	queryset = User.objects.all()