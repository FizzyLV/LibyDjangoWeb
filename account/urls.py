from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("api/token/", views.token_login, name="api-token-login"),
]
