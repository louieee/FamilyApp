from django.http import JsonResponse


def home(request, *args, **kwargs):
	return JsonResponse(data={"message": "Voting App APIs"}, safe=False)
