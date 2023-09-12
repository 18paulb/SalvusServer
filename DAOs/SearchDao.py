import uuid
from datetime import datetime
import logging
import boto3
from salvusbackend.logger import logger
from boto3.dynamodb.conditions import Key, Attr


class SearchDao:

    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
        self.searchTable = self.dynamodb.Table('Searches')

    def insert_search(self, searchText, email, company, typeCode):

        try:
            self.searchTable.put_item(
                Item={
                    "searchId": str(uuid.uuid4()),
                    "searchText": searchText,
                    "email": email,
                    "company": company,
                    "code": typeCode,
                    "date": datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                }
            )
        except Exception as e:
            logging.error(e)  # Assuming logging is set up

    def get_search_history(self, email: str):
        response = self.searchTable.query(
            IndexName='email-index',
            KeyConditionExpression=boto3.dynamodb.conditions.Key('email').eq(email)
        )

        items = response['Items']

        # Sorts the data so that the most recent searches appear first
        sorted_data = sorted(items, key=lambda x: datetime.strptime(x['date'], "%m/%d/%Y, %H:%M:%S"),
                             reverse=True)

        return sorted_data
