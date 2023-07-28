import datetime
import json
import jwt

import bcrypt
from boto3.dynamodb.types import Binary
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from decouple import config

from authentication.database import find_password_by_username, update_user_authtoken, compare_token_to_database
from salvusbackend.logger import logger


# TODO: Do not have csrf_exempt in production
@csrf_exempt
def login(request):
    try:

        body = json.loads(request.body.decode('utf-8'))
        email = body['email']
        password = body['password']

        # Finds the hashed password in the database
        hashedPassword = find_password_by_username(email)

        # Checks to make sure that the password is correct
        success = verify_password(hashedPassword, password)

        # Creates new authtoken and updates it in the database
        authtoken, expDate = generate_authtoken()
        update_user_authtoken(email, authtoken, expDate)

        if success:
            return JsonResponse({"message": "Successfully Logged In", "authtoken": authtoken, "expDate": expDate},
                                status=200)
        else:
            return JsonResponse({"message": "Incorrect Password"}, status=401)

    except Exception as e:
        logger.error(e)
        return JsonResponse({"message": "An error has occurred"}, status=500)


def verify_password(hashed_password, provided_password):
    """Verify a stored password against one provided by user"""
    password = provided_password.encode('utf-8')
    if isinstance(hashed_password[1], Binary):  # check if it's a Binary object
        stored_hashed_password = hashed_password[1]  # get the bytes
        return bcrypt.checkpw(password, stored_hashed_password.value)

    raise Exception("Hashed password is not a Binary object")


def generate_authtoken():
    SECRET_KEY = config('AUTHTOKEN_SECRET_KEY')
    # Create a JWT token with an expiration time of 1 hour
    payload = {"sub": "admin", "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)}
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token, payload["exp"]


def verify_authtoken(email, authtoken):
    try:

        # Finds the hashed password in the database
        return compare_token_to_database(email, authtoken)

    except Exception as e:
        logger.error(e)
        return False