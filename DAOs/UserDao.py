import uuid
from datetime import datetime
import logging
import boto3
import bcrypt

from salvusbackend.logger import logger
from boto3.dynamodb.conditions import Key, Attr


class UserDao:

    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
        self.table = self.dynamodb.Table('Users')

    def register_user(self, email, password, companyName):
        hashedPassword = self.hash_password(password)
        try:
            userId = str(uuid.uuid4())
            self.table.put_item(
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

    def find_password_by_username(self, email):
        try:
            response = self.table.query(
                ProjectionExpression='email, userAuthentication',
                KeyConditionExpression=boto3.dynamodb.conditions.Key('email').eq(email)
            )

            # Convert Into String
            return response['Items'][0]['userAuthentication']['password']
        except Exception as e:
            logger.error(e)
            print(e)

    @staticmethod
    def hash_password(password):
        """Hash a password for storing."""
        password = password.encode('utf-8')  # Passwords should be bytes
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password, salt)
        return salt, hashed_password

    def get_user_by_email(self, email):
        response = self.table.get_item(
            Key={
                'email': email
            }
        )

        return response.get('Item')
