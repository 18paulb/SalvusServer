import json

from django.http import HttpResponse

import trademarkSearch.database as db
import trademarkSearch.textSimilarity as ts
from trademarkSearch.datacleaning import download_and_process_files
from trademarkSearch.models import Trademark, make_trademark_objects
import os
from salvusbackend.logger import logger


# Create your views here.

def markDatabaseSearch(request):
    try:
        inputMark = request.GET.get('query')
        typeCode = request.GET.get('code')

        infringementList = []

        marks = db.get_trademarks_by_code(typeCode)

        ts.judge_exact_match(marks, inputMark, infringementList)
        ts.judge_ratio_fuzzy(marks, inputMark, infringementList)

        return HttpResponse(json.dumps([infringement.to_dict() for infringement in infringementList]),
                            content_type="application/json",
                            status=200)

    except Exception as e:
        logger.error(e)
        return HttpResponse("An error has occured", status=500)

# This code does entire process of downloading, cleaning, and inserting into database, uncomment as needed
# download_and_process_files()

# models = []
# for file in os.listdir():
#     if file.endswith(".xml"):
#         models.extend(make_trademark_objects(file))
#
# print("Inserting into database")
#
# db.insert_into_table(models)
