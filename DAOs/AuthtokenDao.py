import uuid
import datetime
import logging
import boto3
from salvusbackend.logger import logger
from boto3.dynamodb.conditions import Key, Attr


class AuthtokenDao:

    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
        self.table = self.dynamodb.Table('Users')

    def update_user_authtoken(self, email, authtoken, expDate):
        try:
            self.table.update_item(
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

    def find_user_info_by_authtoken(self, authtoken):
        try:
            response = self.table.query(
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

    # def compare_token_to_database(self, email, authtoken):
    #     try:
    #         response = self.table.query(
    #             ProjectionExpression='email, authtoken, expDate',
    #             KeyConditionExpression=boto3.dynamodb.conditions.Key('email').eq(email)
    #         )
    #
    #         # Makes sure authtoken matches and is not expired
    #         datestr = datetime.strptime(response['Items'][0]['expDate'], "%Y-%m-%dT%H:%M:%S.%f")
    #         return (response['Items'][0]['authtoken'] == authtoken and
    #                 datestr > datetime.utcnow())
    #
    #     except Exception as e:
    #         logger.error(e)
    #         print(e)

    # def verify_authtoken(self, email, authtoken):
    #     try:
    #         # Finds the hashed password in the database
    #         return self.compare_token_to_database(email, authtoken)
    #
    #     except Exception as e:
    #         logger.error(e)
    #         return False

    def verify_authtoken(self, authtoken):
        try:
            response = self.table.query(
                IndexName='authtoken-index',  # Name of the Global Secondary Index
                KeyConditionExpression=boto3.dynamodb.conditions.Key('authtoken').eq(authtoken),
            )

            # Makes sure authtoken matches and is not expired
            datestr = response['Items'][0]['expDate']
            # Parse the datetime string from JSON.
            exp_date = datetime.datetime.fromisoformat(datestr)

            return exp_date > datetime.datetime.utcnow()

        except Exception as e:
            logger.error(e.__str__() + "\nInvalid authtoken given")
            print(e.__str__() + "\nInvalid authtoken given")
