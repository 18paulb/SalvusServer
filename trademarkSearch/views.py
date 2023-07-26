import json

from django.http import HttpResponse

import trademarkSearch.database as db
import trademarkSearch.textSimilarity as ts
from trademarkSearch.datacleaning import download_and_process_files


# Create your views here.

def markDatabaseSearch(request):
    try:
        inputMark = request.GET.get('query')
        typeCode = request.GET.get('code')

        infringementList = []

        marks = db.get_trademarks_by_code(typeCode)

        ts.judge_exact_match(marks, inputMark, infringementList)
        ts.judge_ratio_fuzzy(marks, inputMark, infringementList)

        return HttpResponse(json.dumps({'trademarks': [infringement.to_dict() for infringement in infringementList]}),
                            content_type="application/json",
                            status=200)

    except Exception as e:
        print(e)
        return HttpResponse("Error", status=500)


download_and_process_files()
