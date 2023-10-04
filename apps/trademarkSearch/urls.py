from django.urls import path
import apps.trademarkSearch.trademarkviews as trademarkViews

urlpatterns = [
    path('markSearchSame', trademarkViews.same_mark_search, name='mark_search_same'),
]
