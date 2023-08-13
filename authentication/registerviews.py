from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
import json
from authentication.database import register_user
from salvusbackend.logger import logger
from authentication.database import update_user_authtoken
from authentication.loginviews import generate_authtoken


# TODO: Do not have csrf_exempt in production
@csrf_exempt
def register(request):
    try:
        body = json.loads(request.body.decode('utf-8'))
        register_user(body['email'], body['password'], body['company_name'])

        # Creates new authtoken and updates it in the database
        authtoken, expDate = generate_authtoken()
        update_user_authtoken(body['email'], authtoken, expDate)

        return JsonResponse({"message": "Successfully Registered In", "authtoken": authtoken, "expDate": expDate},
                            status=200)
    except Exception as e:
        logger.error(e)
        return JsonResponse({"message": "An error has occurred"}, status=500)
