from django.urls import path
import trademarkSearch.trademarkViews as trademarkViews

urlpatterns = [
    path('markSearchSame', trademarkViews.same_mark_search, name='mark_search_all'),
    path('markSearchAll', trademarkViews.all_mark_search, name='mark_search_same'),
    path('classifyCode', trademarkViews.classifyCode, name='classify_code')
]

