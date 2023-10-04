from django.http import JsonResponse
import apps.trademarkSearch.tasks as tasks
from celery.result import AsyncResult
from DAOs.TrademarkDao import TrademarkDao
import apps.trademarkSearch.textSimilarity as ts


def check_task_status(request):
    task_id = request.GET.get('task_id')
    inputMark = request.GET.get('query')

    task = AsyncResult(task_id)
    response_data = {
        'task_status': task.status,
        'task_id': task.id
    }

    if task.status == 'SUCCESS':
        marks = task.result
        # Convert back into tuples because Redis doesn't support it and it is returned as list of lists
        marks = [tuple(mark) for mark in marks]
        td = TrademarkDao()

        # Give each trademark a score based on closeness to input mark, return that sorted list of infringements
        infringementList = ts.score_similar_trademarks(marks, inputMark)

        # Now we need to retrieve the rest of the data for the trademarks, in order to make sure the response is as quick as possible
        # Only get the data for some of the trademarks right now, and if the user requests
        returnVals = td.get_trademarks_by_serial_number(infringementList)

        response_data = {
            'data': [{'trademark': infringement[0].to_dict(), 'riskLevel': infringement[1]}
                     for infringement in returnVals],
        }
        return JsonResponse(response_data, safe=False, status=200)

    else:
        return JsonResponse(response_data)
