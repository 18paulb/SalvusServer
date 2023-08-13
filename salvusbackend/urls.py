"""salvusbackend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from trademarkSearch import trademarkViews
from authentication import registerviews
from authentication import loginviews

urlpatterns = [
    path('admin/', admin.site.urls),
    path('markSearch', trademarkViews.markDatabaseSearch, name='mark_search'),
    path('register', registerviews.register, name='register'),
    path('login', loginviews.login, name='login'),
    path('classifyCode', trademarkViews.classifyCode, name='classify_code'),
    path('searchHistory', trademarkViews.getSearchHistory, name='search_history')
]
