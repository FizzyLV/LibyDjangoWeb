from django.urls import path
from . import views

urlpatterns = [
    path("api/token/", views.token_login, name="api-token-login"),
    path("api/token/logout/", views.token_logout, name="api-token-logout"),
    path("api/token/deleteac/", views.tokenDeleteAccount, name="api-token-deleteac"),
    path("api/token/register/", views.tokenRegister, name="api-token-register"),
    path("api/token/verify/", views.tokenVerify , name="api-token-register"),
]
