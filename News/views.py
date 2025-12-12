from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from News.models import newsItems
from authTokenHandler.models import isTokenValid
from account.decorators import login_required

@login_required
def news(request):
    newsObject = newsItems.objects.all() 

    newsContext = {
        'news': newsObject,
        'admin' : request.session.get('isAdmin', False)
    }

    return render(request, 'news/news.html', newsContext)


@login_required
def addNews(request):
    if request.method == 'POST' and request.session.get('isAdmin', False):
        reqPost = request.POST
        title = reqPost.get('title', '')
        description = reqPost.get('description', '')
        image = request.FILES.get('image', None)
        authorId = request.session.get('userId', None)

        if all([title, description, image, authorId]):
            newsItems.objects.create(
                author_id=authorId,
                title=title,
                description=description,
                image=image
            )
            return JsonResponse({'detail': 'News added successfully'}, status=201)
        else:
            return JsonResponse({'detail': 'All fields are required'}, status=400)

    return JsonResponse({'detail': 'Forbidden'}, status=403)



        
@csrf_exempt
def returnNewsItems(request):
    if request.method != 'GET':
        return JsonResponse({'detail': 'Method not allowed'}, status=405)

    token = request.headers.get('authorization')

    if not token or not isTokenValid(token):
        return JsonResponse({'detail': 'Invalid or missing token'}, status=401)
    
    # offset = int(request.GET.get('offset', 0))
    # if offset < 0:
    #     return JsonResponse({'detail': 'Invalid offset'}, status=400)
    
    news_list = []
    for news_item in newsItems.objects.select_related('author').all():
        news_list.append({
            'id': news_item.id,
            'title': news_item.title,
            'description': news_item.description,
            'imageUrl': request.build_absolute_uri(news_item.image.url) if news_item.image else None,
            'authorName': f"{news_item.author.firstName} {news_item.author.lastName}",
            'email': news_item.author.email,
            'publishedAt': int(news_item.publishedAt.timestamp()),
        })

    return JsonResponse({'news': news_list}, status=200)