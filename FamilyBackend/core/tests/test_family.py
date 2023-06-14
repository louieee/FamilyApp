from django.http import JsonResponse


def home(request, *args, **kwargs):
	return JsonResponse(data={"message": "Family APIs"}, safe=False)
