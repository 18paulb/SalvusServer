from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from register.database import register_user
from salvusbackend.logger import logger


# TODO: Do not have csrf_exempt in production
@csrf_exempt
def register(request):
    try:
        body = json.loads(request.body.decode('utf-8'))
        register_user(body['username'], body['password'], body['company_name'], body['email'])

        return HttpResponse("Successfully Registered", 200)
    except Exception as e:
        logger.error(e)
        return HttpResponse("An error has occurred", 500)
