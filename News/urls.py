from django.urls import path
from . import views

urlpatterns = [
    path("api/token/news/", views.returnNewsItems, name="api-news-return"),
    path("home/", views.news, name="home"),
    path("add_news/", views.addNews, name="add_news"),
]
