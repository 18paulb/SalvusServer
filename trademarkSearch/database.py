import boto3
from trademarkSearch.models import Trademark, make_trademark_objects
import uuid
from salvusbackend.logger import logger
from boto3.dynamodb.conditions import Key
from datetime import datetime

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
table = dynamodb.Table('Trademarks')
searchTable = dynamodb.Table('Searches')

"""
This function takes in a list of trademark objects and inserts them into the database
"""


def insert_into_table(trademarks: list):
    i = 1
    with table.batch_writer() as batch:
        for trademark in trademarks:
            logger.info(f"Inserting batch {i} of {len(trademarks)} into database")
            print(f"Inserting batch {i} of {len(trademarks)} into database")
            try:
                if trademark.codes is None or len(trademark.codes) == 0:
                    batch.put_item(
                        Item={
                            "mark_identification": trademark.mark_identification,
                            "serial_number": trademark.serial_number,
                            "case_owners": trademark.case_owners,
                            "date_filed": trademark.date_filed,
                            "code": None,
                            "activeStatus": trademark.activeStatus,
                            "case_file_descriptions": trademark.case_file_descriptions
                        }
                    )

                elif len(trademark.codes) > 1:
                    for code in trademark.codes:
                        batch.put_item(
                            Item={
                                "mark_identification": trademark.mark_identification,
                                "serial_number": trademark.serial_number,
                                "case_owners": trademark.case_owners,
                                "date_filed": trademark.date_filed,
                                "code": code,
                                "activeStatus": trademark.activeStatus,
                                "case_file_descriptions": trademark.case_file_descriptions
                            }
                        )
                else:
                    batch.put_item(
                        Item={
                            "mark_identification": trademark.mark_identification,
                            "serial_number": trademark.serial_number,
                            "case_owners": trademark.case_owners,
                            "date_filed": trademark.date_filed,
                            "code": trademark.codes[0],
                            "activeStatus": trademark.activeStatus,
                            "case_file_descriptions": trademark.case_file_descriptions
                        }
                    )
            except Exception as e:
                logger.error(e)
                continue
            i += 1


def save_search_into_table(searchText, email, company, typeCode):
    # Eventually figure out how to include email and company (through GET request) (Actually just use the authtoken
    # in the header)
    try:
        searchTable.put_item(
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
        logger.error(e)


"""
This function takes in a code and returns queries the database for all trademarks with that code
"""


def get_trademarks_by_code(code: str):
    response = table.query(
        IndexName='code-index',
        KeyConditionExpression=boto3.dynamodb.conditions.Key('code').eq(code)
    )

    items = response['Items']
    trademarks = []

    for trademark in items:
        trademarks.append(
            Trademark(
                trademark.get("mark_identification"),
                trademark.get("serial_number"),
                trademark.get("code"),
                trademark.get("case_file_descriptions"),
                trademark.get("case_owners"),
                trademark.get("date_filed"),
                trademark.get("activeStatus")
            )
        )

    return trademarks


def get_search_history(email: str):
    response = searchTable.query(
        IndexName='email-index',
        KeyConditionExpression=boto3.dynamodb.conditions.Key('email').eq(email)
    )

    items = response['Items']

    sorted_data = sorted(items, key=lambda x: datetime.strptime(x['date'], "%m/%d/%Y, %H:%M:%S"), reverse=True)

    return sorted_data
