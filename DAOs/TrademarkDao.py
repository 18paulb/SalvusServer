import json
import boto3
from trademarkSearch.TrademarkModel import Trademark
from salvusbackend.logger import logger
from boto3.dynamodb.conditions import Key, Attr
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
                    if trademark.descriptions_and_codes is None or len(trademark.descriptions_and_codes) == 0:
                        batch.put_item(
                            Item={
                                "mark_identification": trademark.mark_identification,
                                "serial_number": trademark.serial_number,
                                "case_owners": trademark.case_owners,
                                "date_filed": trademark.date_filed,
                                "code": None,
                                "activeStatus": trademark.activeStatus,
                                "description": None,
                                "disclaimers": trademark.disclaimers
                            }
                        )

                    elif len(trademark.descriptions_and_codes) >= 1:
                        for desc_and_code in trademark.descriptions_and_codes:
                            description = desc_and_code[0]
                            code = desc_and_code[1]

                            batch.put_item(
                                Item={
                                    "mark_identification": trademark.mark_identification,
                                    "serial_number": trademark.serial_number,
                                    "case_owners": trademark.case_owners,
                                    "date_filed": trademark.date_filed,
                                    "code": code,
                                    "activeStatus": trademark.activeStatus,
                                    "description": description,
                                    "disclaimers": trademark.disclaimers
                                }
                            )
                except Exception as e:
                    logger.error(e)
                    continue
                i += 1

    def search_by_code(self, code: str, activeStatus: str, lastEvaluatedKey: any):
        query_params = {
            "IndexName": 'code-date_filed-index',
            "KeyConditionExpression": boto3.dynamodb.conditions.Key('code').eq(code),
            "FilterExpression": Attr('activeStatus').eq(activeStatus),
            'ScanIndexForward': False,
        }

        if lastEvaluatedKey is not None:
            query_params["ExclusiveStartKey"] = json.loads(lastEvaluatedKey)

        response = self.table.query(**query_params)

        items = response['Items']
        lastKey = response.get('LastEvaluatedKey', None)
        trademarks = []

        for trademark in items:
            description_and_code = (trademark.get("description"), trademark.get("code"))

            trademarks.append(
                Trademark(
                    trademark.get("mark_identification"),
                    trademark.get("serial_number"),
                    description_and_code,
                    trademark.get("disclaimers"),
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
            description_and_code = (trademark.get("description"), trademark.get("code"))

            trademarks.append(
                Trademark(
                    trademark.get("mark_identification"),
                    trademark.get("serial_number"),
                    description_and_code,
                    trademark.get("disclaimers"),
                    trademark.get("case_owners"),
                    trademark.get("date_filed"),
                    trademark.get("activeStatus")
                )
            )

        return [trademarks, lastKey]
