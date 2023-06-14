from django.http import JsonResponse


def home(request, *args, **kwargs):
	return JsonResponse(data={"message": "User APIs"}, safe=False)
