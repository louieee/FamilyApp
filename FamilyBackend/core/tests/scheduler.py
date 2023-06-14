from django.http import JsonResponse


def home(request, *args, **kwargs):
	return JsonResponse(data={"message": "Scheduler APP APIs"}, safe=False)
