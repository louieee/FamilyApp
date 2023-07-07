import asyncio
import json

import websockets
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken, Token


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


async def websocket_client(url, payload):
	async with websockets.connect(url) as websocket:
		await websocket.send(payload)
		await websocket.recv()


def get_or_create_eventloop():
	try:
		return asyncio.get_event_loop()
	except RuntimeError as ex:
		if "There is no current event loop in thread" in str(ex):
			loop = asyncio.new_event_loop()
			asyncio.set_event_loop(loop)
			return asyncio.get_event_loop()


def send_ws(user, family, socket_type, action, payload):
	refresh = RefreshToken.for_user(user)
	url = f"ws://websocket:8001/ws/{socket_type}/{family}/{refresh.access_token}/"
	payload = dict(action=action, payload=payload)
	payload = json.dumps(payload)
	loop = get_or_create_eventloop()
	loop.run_until_complete(websocket_client(url, payload))
	return
