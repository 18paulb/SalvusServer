from django.urls import path
import trademarkSearch.trademarkviews as trademarkViews
from authentication import loginviews
from authentication import registerviews

urlpatterns = [
    path('login', loginviews.login, name='login'),
    path('register', registerviews.register, name='register'),
    path('verify-authtoken', loginviews.authenticate, name='authenticate')

    # other routes specific to app1
]


