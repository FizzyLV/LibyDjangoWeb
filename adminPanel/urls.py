from django.urls import path, include
from . import views
import django_eventstream
from account.decorators import login_required

urlpatterns = [
    path("adminstrator/denied", views.adminDenied, name="adminDenied"),
    path("adminstrator/", views.admin, name="admin"),
    path('news/edit/<int:id>/', views.editNews, name='edit_news')
]