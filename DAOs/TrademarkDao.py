import json
import boto3
from apps.trademarkSearch.TrademarkModel import Trademark
from salvusbackend.logger import logger
from boto3.dynamodb.conditions import Key, Attr
import threading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor


def make_trademarks_from_table_results(items):
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

    return trademarks


class TrademarkDao:

    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
        self.table_name = 'Trademarks'
        self.table = self.dynamodb.Table(self.table_name)
        self.counter = 0  # Shared counter
        self.lock = threading.Lock()  # Lock to make updating the counter thread-safe

    def insert_batch(self, trademarks: list):
        i = 1
        with self.table.batch_writer() as batch:
            for trademark in trademarks:
                logger.info(f"Inserting batch {i} of {len(trademarks)} into database")
                print(f"Inserting batch {i} of {len(trademarks)} into database")

                # TODO: Every registration I have looked at in who has had date_filed = '' was not found in TESS so I am skipping the upload now. Make sure to go through USPTO dat again
                # TODO: To make sure that we are not missing anything
                if trademark.date_filed == '':
                    continue

                try:
                    if trademark.description_and_code is None or len(trademark.description_and_code) == 0:
                        batch.put_item(
                            Item={
                                "mark_identification": trademark.mark_identification if trademark.mark_identification is not None else "",
                                "serial_number": trademark.serial_number if trademark.serial_number is not None else "",
                                "case_owners": trademark.case_owners if trademark.case_owners is not None else [],
                                "date_filed": trademark.date_filed if trademark.date_filed is not None else "",
                                "code": None,
                                "activeStatus": trademark.activeStatus if trademark.activeStatus is not None else "",
                                "description": None,
                                "disclaimers": trademark.disclaimers if trademark.activeStatus is not None else []
                            }
                        )

                    elif len(trademark.description_and_code) >= 1:
                        for desc_and_code in trademark.description_and_code:
                            description = desc_and_code[0]
                            code = desc_and_code[1]

                            batch.put_item(
                                Item={
                                    "mark_identification": trademark.mark_identification if trademark.mark_identification is not None else "",
                                    "serial_number": trademark.serial_number if trademark.serial_number is not None else "",
                                    "case_owners": trademark.case_owners if trademark.case_owners is not None else [],
                                    "date_filed": trademark.date_filed if trademark.date_filed is not None else "",
                                    "code": code if code is not None else "",
                                    "activeStatus": trademark.activeStatus if trademark.activeStatus is not None else "",
                                    "description": description if description is not None else "",
                                    "disclaimers": trademark.disclaimers if trademark.activeStatus is not None else []
                                }
                            )
                except Exception as e:
                    logger.error(e)
                    continue
                i += 1

    # Consider having this return all the codes of a trademark and not just one
    def search_all(self, activeStatus: str):
        # The exclusiveStartKey and the lastEvaluatedKey allows for pagination of search results of scan returns too much data
        query_params = {
            "FilterExpression": Attr('activeStatus').eq(activeStatus),
        }

        return self.query_dynamodb(query_params)

    """
    What this method does is it will query using the fast-retrival-code-index, which basically returns fewer data from each object from the table
    so that we can query faster and get more results from each read
    """

    def search_by_code(self, code: str):

        # We are going to use multithreading to make this faster
        queries = [
            # Gets all trademarks before 2000
            {
                "IndexName": 'fast-code-date_filed-index',
                "KeyConditionExpression": Key('code').eq(code) & Key('date_filed').begins_with(
                    '19')
            },
            # Gets all trademarks during the 2000s
            {
                "IndexName": 'fast-code-date_filed-index',
                "KeyConditionExpression": Key('code').eq(code) & Key('date_filed').begins_with(
                    '200')
            },
            # Gets all trademarks during the 2010s
            {
                "IndexName": 'fast-code-date_filed-index',
                "KeyConditionExpression": Key('code').eq(code) & Key('date_filed').begins_with(
                    '201')
            },
            # Gets all trademarks during the 2020s
            {
                "IndexName": 'fast-code-date_filed-index',
                "KeyConditionExpression": Key('code').eq(code) & Key('date_filed').begins_with(
                    '202')
            },
        ]

        overallItems = []

        with ThreadPoolExecutor() as executor:
            future_results = [executor.submit(self.query_dynamodb, query_param) for query_param in queries]

        for future in future_results:
            result = future.result()
            if result is not None:
                overallItems.extend(result)
        print("Table queries done")

        return overallItems

    def query_dynamodb(self, query_param):
        overallItems = []
        while True:

            try:
                response = self.table.query(**query_param)
                overallItems.extend(response['Items'])  # Extend rather than append to flatten the list

                lastKey = response.get('LastEvaluatedKey', None)

                if lastKey is None:
                    break

                query_param["ExclusiveStartKey"] = lastKey

            except Exception as e:
                logger.error(e)
                break

        return [(item['serial_number'], item['code'], item['mark_identification']) for item in overallItems]

    """
    This will need to get moved around to be cleaner code, however each item in serial_numbers_and_codes
    will be a tuple of ((trademarkInfo), riskLevel set earlier)
    """

    def get_trademarks_by_serial_number(self, serial_numbers_and_codes: list):
        # Grabs first thousand trademarks to return from the list of infringements

        total_items = []

        # Not returning any items with new elements
        first_thousand = serial_numbers_and_codes[0:1000]
        # This for loop will make sure we get 1000 results
        for i in range(0, 10):
            start_index = i * 100
            end_index = start_index + 100
            keys_to_fetch = [
                {
                    "serial_number": partition,
                    "code": sort_key,
                }
                for ((partition, sort_key, _), _) in first_thousand[start_index:end_index]
            ]

            # Convert the keys into the format that DynamoDB expects
            request_items = {
                self.table_name: {
                    'Keys': keys_to_fetch,
                    'ProjectionExpression': "serial_number, code, activeStatus, case_owners, date_filed, description, disclaimers, mark_identification"
                }
            }

            # Use BatchGetItem to fetch the items
            response = self.dynamodb.batch_get_item(RequestItems=request_items)
            total_items.extend(response['Responses'][self.table_name])

        trademarks = make_trademarks_from_table_results(total_items)

        trademarks_with_ratings = []
        for item in trademarks:
            for trademark in first_thousand:
                if item.serial_number == trademark[0][0]:
                    trademarks_with_ratings.append((item, trademark[1]))

        return trademarks_with_ratings
