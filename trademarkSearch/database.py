import boto3
from trademarkSearch.models import Trademark, make_trademark_objects
import uuid
from salvusbackend.logger import logger

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
table = dynamodb.Table('Trademarks')
searchTable = dynamodb.Table('Searches')

"""
This function takes in a list of trademark objects and inserts them into the database
"""


def insert_into_table(trademarks: list):
    # TODO: As of right now some case_file_descriptions are too large to insert into the database
    with table.batch_writer() as batch:
        for trademark in trademarks:
            try:
                if trademark.codes is None or len(trademark.codes) == 0:
                    batch.put_item(
                        Item={
                            "mark_identification": trademark.mark_identification,
                            "serial_number": trademark.serial_number,
                            "case_owners": trademark.case_owners,
                            "date_filed": trademark.date_filed,
                            "code": None,
                            "activeStatus": trademark.activeStatus
                            # "case_file_descriptions": trademark.case_file_descriptions
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
                                "activeStatus": trademark.activeStatus
                                # "case_file_descriptions": trademark.case_file_descriptions
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
                print(e)
                continue


def save_search_into_table(searchText, email, company):
    # Eventually figure out how to include email and company (through GET request) (Actually just use the authtoken
    # in the header)
    try:
        searchTable.put_item(
            Item={
                "searchId": str(uuid.uuid4()),
                "searchText": searchText,
            }
        )
    except Exception as e:
        logger.error(e)
        print(e)


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
        # TODO: Eventually we will need to include case_file_descriptions somehow
        tmp = Trademark(trademark["mark_identification"], trademark["serial_number"], trademark["code"], [],
                        trademark["case_owners"], trademark["date_filed"])

        trademarks.append(tmp)

    return trademarks
