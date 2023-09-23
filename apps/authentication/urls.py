from django.urls import path
from apps.authentication import registerviews, loginviews

urlpatterns = [
    path('login', loginviews.login, name='login'),
    path('register', registerviews.register, name='register'),
    path('verify-authtoken', loginviews.authenticate, name='authenticate')
]
