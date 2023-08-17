import boto3
import uuid
from salvusbackend.logger import logger
import bcrypt
from boto3.dynamodb.types import Binary
from datetime import datetime
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
table = dynamodb.Table('Users')


def register_user(email, password, companyName):
    hashedPassword = hash_password(password)
    try:
        userId = str(uuid.uuid4())
        table.put_item(
            Item={
                "email": email,
                "userId": userId,
                "company_name": companyName,

                "userAuthentication": {
                    "password": hashedPassword,
                }
            }
        )

    except Exception as e:
        logger.error(e)
        print(e)


def find_password_by_username(email):
    try:
        response = table.query(
            ProjectionExpression='email, userAuthentication',
            KeyConditionExpression=boto3.dynamodb.conditions.Key('email').eq(email)
        )

        # Convert Into String
        return response['Items'][0]['userAuthentication']['password']
    except Exception as e:
        logger.error(e)
        print(e)


def find_userInfo_by_authtoken(authtoken):
    try:
        response = table.query(
            IndexName='authtoken-index',  # Name of the Global Secondary Index
            KeyConditionExpression=boto3.dynamodb.conditions.Key('authtoken').eq(authtoken),
        )

        # Convert Into String
        for item in response['Items']:
            if item['authtoken'] == authtoken:
                return item['email'], item['company_name']

    except Exception as e:
        logger.error(e)
        print(e)


def update_user_authtoken(email, authtoken, expDate):
    try:
        table.update_item(
            Key={
                'email': email
            },
            UpdateExpression="SET authtoken = :a, expDate = :b",
            ExpressionAttributeValues={

                ':a': authtoken,
                ':b': expDate.isoformat()
            }
        )
    except Exception as e:
        logger.error(e)
        print(e)


def compare_token_to_database(email, authtoken):
    try:
        response = table.query(
            ProjectionExpression='email, authtoken, expDate',
            KeyConditionExpression=boto3.dynamodb.conditions.Key('email').eq(email)
        )

        # Makes sure authtoken matches and is not expired
        datestr = datetime.strptime(response['Items'][0]['expDate'], "%Y-%m-%dT%H:%M:%S.%f")
        return (response['Items'][0]['authtoken'] == authtoken and
                datestr > datetime.utcnow())

    except Exception as e:
        logger.error(e)
        print(e)


def hash_password(password):
    """Hash a password for storing."""
    password = password.encode('utf-8')  # Passwords should be bytes
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password, salt)
    return salt, hashed_password
