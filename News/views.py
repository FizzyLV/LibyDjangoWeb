from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from News.models import newsItems
from authTokenHandler.models import isTokenValid
from account.decorators import login_required
from django_eventstream import send_event
import django_eventstream
from django.db.models import Max    

@login_required
def news(request):
    newsObject = newsItems.objects.all() 

    newsContext = {
        'news': newsObject,
        'admin': request.session.get('isAdmin', False)
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
            news_item = newsItems.objects.create(
                author_id=authorId,
                title=title,
                description=description,
                image=image
            )
            
            # Send SSE event with the newly created news item
            send_event("News", "new_news", {
                'id': news_item.id,
                'title': news_item.title,
                'description': news_item.description,
                'imageUrl': request.build_absolute_uri(news_item.image.url) if news_item.image else None,
                'authorName': f"{news_item.author.firstName} {news_item.author.lastName}",
                'email': news_item.author.email,
                'publishedAt': int(news_item.publishedAt.timestamp())
            })
            
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
    
    last_id = request.headers.get('lastId', '0')
    
    try:
        last_id = int(last_id)
        if last_id < 0:
            return JsonResponse({'detail': 'Invalid lastId'}, status=400)
    except (ValueError, TypeError):
        return JsonResponse({'detail': 'Invalid lastId format'}, status=400)

    if last_id > (newsItems.objects.aggregate(max_id=Max('id'))['max_id'] or 0):
        return JsonResponse({'detail': 'lastId exceeds database'}, status=400)

    news_list = []
    for news_item in newsItems.objects.select_related('author').filter(id__gt=last_id).order_by('id'):
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


@csrf_exempt
def news_events(request):
    # Check session auth first (for web)
    if request.session.get('isAuthenticated'):
        return django_eventstream.views.events(request, "News")
    
    token = request.headers.get('authorization')
    if token and isTokenValid(token):
        return django_eventstream.views.events(request, "News")
    
    # No valid auth
    return JsonResponse({'detail': 'Unauthorized'}, status=401)