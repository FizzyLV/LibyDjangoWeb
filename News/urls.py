from django.urls import path, include
from . import views
import django_eventstream

urlpatterns = [
    path("api/token/news/", views.returnNewsItems, name="api-news-return"),
    path("home/", views.news, name="home"),
    path("news/add/", views.addNews, name="add_news"),
    path("events/news/", views.news_events, {"channels": ["News"]}),
    path('api/token/addnews/', views.addNews, name='add_news_token'),
    path('api/token/deletenews/<int:id>/', views.deleteNewsItem, name='delete_news_item'),
    path('news/delete/<int:id>/', views.deleteNews, name='delete_news'),  # Web-based delete
]