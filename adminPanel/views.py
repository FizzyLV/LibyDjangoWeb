from django.shortcuts import render
from account.decorators import login_required
from adminPanel.decorators import admin_required
from News.models import newsItems

@login_required
@admin_required
def admin(request):
    newsObject = newsItems.objects.all() 

    newsContext = {
        'news': newsObject,
    }

    return render(request, 'admin.html', newsContext)


def adminDenied(request):
    return render(request, 'notAdmin.html')


    