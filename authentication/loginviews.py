import datetime
import json
import jwt
import bcrypt
from boto3.dynamodb.types import Binary
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from salvusbackend.logger import logger
from DAOs.AuthtokenDao import AuthtokenDao
from DAOs.UserDao import UserDao
from dotenv import load_dotenv
import os


# TODO: Do not have csrf_exempt in production
@csrf_exempt
def login(request):
    try:

        body = json.loads(request.body.decode('utf-8'))
        email = body['email']
        password = body['password']

        userDao = UserDao()
        authtokenDao = AuthtokenDao()

        # Finds the hashed password in the database
        hashedPassword = userDao.find_password_by_username(email)

        if hashedPassword is None:
            return JsonResponse({"message": "Username not found"}, status=401)

        # Checks to make sure that the password is correct
        success = verify_password(hashedPassword, password)

        if success:
            # Creates new authtoken and updates it in the database
            authtoken, expDate = generate_authtoken()
            authtokenDao.update_user_authtoken(email, authtoken, expDate)

            return JsonResponse({"message": "Successfully Logged In", "authtoken": authtoken, "expDate": expDate},
                                status=200)
        else:
            return JsonResponse({"message": "Incorrect Password"}, status=401)

    except Exception as e:
        logger.error("Error in login: ", e)
        return JsonResponse({"message": "An error has occurred"}, status=500)


def verify_password(hashed_password, provided_password):
    """Verify a stored password against one provided by user"""
    password = provided_password.encode('utf-8')
    if isinstance(hashed_password[1], Binary):  # check if it's a Binary object
        stored_hashed_password = hashed_password[1]  # get the bytes
        return bcrypt.checkpw(password, stored_hashed_password.value)

    raise Exception("Hashed password is not a Binary object")


def generate_authtoken():
    load_dotenv()
    SECRET_KEY = os.environ.get('AUTHTOKEN_SECRET_KEY')
    # Create a JWT token with an expiration time of 24 hour
    payload = {"sub": "user", "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)}
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token, payload["exp"]

