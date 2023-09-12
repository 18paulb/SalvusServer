import json
import boto3
from trademarkSearch.models import Trademark
from salvusbackend.logger import logger
from boto3.dynamodb.conditions import Key, Attr
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading


class TrademarkDao:

    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
        self.table = self.dynamodb.Table('Trademark')
        self.counter = 0  # Shared counter
        self.lock = threading.Lock()  # Lock to make updating the counter thread-safe

    def insert_batch(self, trademarks: list):
        i = 1
        with self.table.batch_writer() as batch:
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

    def search_by_code(self, code: str, activeStatus: str, lastEvaluatedKey: any):
        query_params = {
            "IndexName": 'code-index',
            "KeyConditionExpression": boto3.dynamodb.conditions.Key('code').eq(code),
            "FilterExpression": Attr('activeStatus').eq(activeStatus),
        }

        if lastEvaluatedKey is not None:
            query_params["ExclusiveStartKey"] = json.loads(lastEvaluatedKey)

        response = self.table.query(**query_params)

        items = response['Items']
        lastKey = response.get('LastEvaluatedKey', None)
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

        return trademarks, lastKey

    # Consider having this return all the codes of a trademark and not just one
    def search_all(self, activeStatus: str, lastEvaluatedKey: any):
        # The exclusiveStartKey and the lastEvaluatedKey allows for pagination of search results of scan returns too much data
        query_params = {
            "FilterExpression": Attr('activeStatus').eq(activeStatus),
        }

        if lastEvaluatedKey is not None:
            query_params["ExclusiveStartKey"] = json.loads(lastEvaluatedKey)

        response = self.table.scan(**query_params)

        items = response['Items']
        lastKey = response.get('LastEvaluatedKey', None)
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

        return [trademarks, lastKey]
