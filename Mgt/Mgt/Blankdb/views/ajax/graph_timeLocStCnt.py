from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def page(request):

	return JsonResponse("{hi: hello!!}", safe=False)
