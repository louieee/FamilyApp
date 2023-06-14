from django.http import JsonResponse


def home(request, *args, **kwargs):
	return JsonResponse(data={"message": "Time Table APP APIs"}, safe=False)
