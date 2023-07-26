import boto3
from models import Trademark
from jsonify import load_in_json
from models import make_trademark_objects

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
table = dynamodb.Table('Trademarks')

"""
This function takes in a list of trademark objects and inserts them into the database
"""
def insert_into_table(trademarks: list):

    #TODO: Eventually we will need to include case_file_descriptions somehow
    with table.batch_writer() as batch:
        for trademark in trademarks:

            try:
                if trademark.codes == None or len(trademark.codes) == 0:
                        batch.put_item(
                            Item={
                                "mark_identification": trademark.mark_identification,
                                "serial_number": trademark.serial_number,
                                "case_owners": trademark.case_owners,
                                "date_filed": trademark.date_filed,
                                "code": None,
                                "activeStatus": trademark.activeStatus
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
                            "activeStatus": trademark.activeStatus
                        }
                    )
            except Exception as e:
                print(e)
                continue


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
        tmp = Trademark(trademark["mark_identification"], trademark["serial_number"], trademark["code"], [], trademark["case_owners"], trademark["date_filed"])

        trademarks.append(tmp)

    return trademarks


trademarks = make_trademark_objects(open("cleaned-10.xml", "r"))

#This is just to make sure the database doen't get too big
if len(trademarks) > 100:
    trademarks = trademarks[0:100]

insert_into_table(trademarks)