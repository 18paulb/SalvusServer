from celery import shared_task
from DAOs.TrademarkDao import TrademarkDao


@shared_task
def background_search_by_code(code):
    # Your long-running task logic here
    td = TrademarkDao()
    return td.search_by_code(code)
