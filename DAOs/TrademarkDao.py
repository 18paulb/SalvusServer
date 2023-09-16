import json
import boto3
from trademarkSearch.TrademarkModel import Trademark
from salvusbackend.logger import logger
from boto3.dynamodb.conditions import Key, Attr
import threading


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
        self.table_name = 'Trademark'
        self.table = self.dynamodb.Table(self.table_name)
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

                    elif len(trademark.descriptions_and_codes) >= 1:
                        for desc_and_code in trademark.descriptions_and_codes:
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

        trademarks = make_trademarks_from_table_results(items)

        return [trademarks, lastKey]

    """
    What this method does is it will query using the fast-retrival-code-index, which basically returns fewer data from each object from the table
    so that we can query faster and get more results from each read
    """

    def search_by_code(self, code: str):

        query_params = {
            "IndexName": 'fast-retrieval-code-index',
            "KeyConditionExpression": boto3.dynamodb.conditions.Key('code').eq(code),
        }

        overallItems = []

        i = 0
        while True:

            print("Number of table queries: ", i)
            try:
                response = self.table.query(**query_params)
                overallItems.extend(response['Items'])  # Extend rather than append to flatten the list

                lastKey = response.get('LastEvaluatedKey', None)

                if lastKey is None:
                    break

                query_params["ExclusiveStartKey"] = lastKey
                i += 1

            except Exception as e:
                logger.error(e)
                break

        trademarks = [(item['serial_number'], item['code'], item['mark_identification']) for item in overallItems]

        return trademarks

    """
    This will need to get moved around to be cleaner code, however each item in serial_numbers_and_codes
    will be a tuple of ((trademarkInfo), riskLevel set earlier)
    """

    def test_get_trademarks_by_serial_number(self, serial_numbers_and_codes: list):
        # Grabs first thousand trademarks to return from the list of infringements

        total_items = []

        # FIXME: The thing with this is it doesn't preserve the order of most at risk
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
                    'Keys': keys_to_fetch
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
