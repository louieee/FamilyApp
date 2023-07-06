from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken


def obtain_tokens(username, password):
	# Create a token obtain serializer instance
	data = {'username': username, 'password': password}
	serializer = TokenObtainPairSerializer(data=data)
	serializer.is_valid(raise_exception=True)
	tokens = serializer.validated_data

	# Generate a refresh token
	refresh = RefreshToken.for_user(serializer.user)

	# Return the refresh token and access token
	return {
		'refresh_token': str(refresh),
		'access_token': str(tokens['access']),
	}


def get_access_token(refresh_token):
	# Create a token refresh serializer instance
	data = {'refresh': refresh_token}
	serializer = TokenRefreshSerializer(data=data)
	serializer.is_valid(raise_exception=True)
	tokens = serializer.validated_data
	return str(tokens['access'])


def get_family(request):
	return request.META.get("HTTP_FAMILY")


