from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from authentication.database import register_user
from salvusbackend.logger import logger


# TODO: Do not have csrf_exempt in production
@csrf_exempt
def register(request):
    try:
        body = json.loads(request.body.decode('utf-8'))
        register_user(body['email'], body['password'], body['company_name'])

        return JsonResponse({"message": "Successfully Registered"}, status=200)
    except Exception as e:
        logger.error(e)
        return JsonResponse({"message": "An error has occurred"}, status=500)
