from django.urls import path
from . import views

urlpatterns = [
    path("api/token/", views.token_login, name="api-token-login"),
    path("api/token/logout/", views.token_logout, name="api-token-logout"),
]
