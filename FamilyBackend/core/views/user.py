from rest_framework.viewsets import ModelViewSet

from core.models import User
"""
endpoint to create a family through a signup
endpoint to invite users into a family
endpoint to accept an invite into a family
endpoint to login into a family
endpoint to update profile
"""

class UserAPI(ModelViewSet):
	queryset = User.objects.all()
