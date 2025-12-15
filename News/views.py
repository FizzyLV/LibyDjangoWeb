from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from News.models import newsItems
from authTokenHandler.models import isTokenValid, getUserByToken
from account.decorators import login_required
from adminPanel.decorators import admin_required
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
    if not token:
        return JsonResponse({'detail': 'Token required'}, status=400)
    
    user = getUserByToken(token)
    if not user:
        return JsonResponse({'detail': 'Invalid or expired token'}, status=401)
    
    # Get lastModified timestamp from headers
    last_modified = request.headers.get('lastmodified', '0')
    
    try:
        last_modified = int(last_modified)
        if last_modified < 0:
            return JsonResponse({'detail': 'Invalid lastModified'}, status=400)
    except (ValueError, TypeError):
        return JsonResponse({'detail': 'Invalid lastModified format'}, status=400)

    # Convert timestamp to datetime
    from datetime import datetime
    if last_modified > 0:
        last_modified_dt = datetime.fromtimestamp(last_modified)
    else:
        last_modified_dt = datetime.fromtimestamp(0)

    # Get items that were created or modified after the last modified timestamp
    items_queryset = newsItems.objects.select_related('author').filter(
        lastModifiedAt__gt=last_modified_dt
    ).order_by('lastModifiedAt')
    
    print(f"DEBUG: Items found modified after {last_modified_dt}: {items_queryset.count()}")

    news_list = []
    for news_item in items_queryset:
        print(f"DEBUG: Processing item ID {news_item.id}")
        
        # Handle null author
        if news_item.author:
            author_name = f"{news_item.author.firstName} {news_item.author.lastName}"
            author_email = news_item.author.email
        else:
            author_name = "Unknown Author"
            author_email = "no-email@example.com"
        
        news_list.append({
            'id': news_item.id,
            'title': news_item.title,
            'description': news_item.description,
            'imageUrl': request.build_absolute_uri(news_item.image.url) if news_item.image else None,
            'authorName': author_name,
            'email': author_email,
            'publishedAt': int(news_item.publishedAt.timestamp()),
            'lastModifiedAt': int(news_item.lastModifiedAt.timestamp()),
        })

    print(f"DEBUG: Returning {len(news_list)} items")
    return JsonResponse({'news': news_list}, status=200)


@csrf_exempt
def news_events(request, channels=None, **kwargs):
    # Session auth (web)
    if request.session.get('isAuthenticated'):
        return django_eventstream.views.events(
            request,
            channels=channels
        )

    # Token auth (mobile / API)
    token = request.headers.get('Authorization')
    if token and isTokenValid(token):
        return django_eventstream.views.events(
            request,
            channels=channels
        )

    return JsonResponse({'detail': 'Unauthorized'}, status=401)

@csrf_exempt
def addNews(request):
    if request.method != 'POST':
        return JsonResponse({'detail': 'Method not allowed'}, status=405)
    
    # Check for token-based auth (mobile)
    token = request.headers.get('authorization')
    user = None
    is_admin = False
    
    if token and isTokenValid(token):
        from authTokenHandler.models import getUserByToken
        user = getUserByToken(token)
        is_admin = user.isAdmin if user else False
    # Check for session-based auth (web)
    elif request.session.get('isAuthenticated'):
        is_admin = request.session.get('isAdmin', False)
        user_id = request.session.get('userId', None)
        if user_id:
            from account.models import Account
            user = Account.objects.get(id=user_id)
    
    if not is_admin or not user:
        return JsonResponse({'detail': 'Admin access required'}, status=403)
    
    # Get data
    title = request.POST.get('title', '').strip()
    description = request.POST.get('description', '').strip()
    image = request.FILES.get('image', None)
    
    # Validation
    if not title or not description:
        return JsonResponse({'detail': 'Title and description are required'}, status=400)
    
    if not image:
        return JsonResponse({'detail': 'Image is required'}, status=400)
    
    # Create news item
    news_item = newsItems.objects.create(
        author=user,
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
    
    return JsonResponse({
        'detail': 'News added successfully',
    }, status=201)


@csrf_exempt
def deleteNewsItem(request, id):
    if request.method != 'DELETE':
        return JsonResponse({'detail': 'Method not allowed'}, status=405)
    
    token = request.headers.get('authorization')
    if not token:
        return JsonResponse({'detail': 'Token required'}, status=400)
    
    user = getUserByToken(token)
    if not user:
        return JsonResponse({'detail': 'Invalid or expired token'}, status=401)
    
    if not user.isAdmin:
        return JsonResponse({'detail': 'Admin access required'}, status=403)
    
    try:
        news_item = newsItems.objects.get(id=id)
    except newsItems.DoesNotExist:
        return JsonResponse({'detail': 'News item not found'}, status=404)
    
    news_item.delete()
    
    return JsonResponse({
        'message': 'News item deleted successfully',
        'id': id
    }, status=200)

@admin_required
@login_required
def deleteNews(request, id):
    if request.method != 'POST':
        return JsonResponse({'detail': 'Method not allowed'}, status=405)
    
    if not request.session.get('isAdmin', False):
        return JsonResponse({'detail': 'Admin access required'}, status=403)
    
    try:
        news_item = newsItems.objects.get(id=id)
    except newsItems.DoesNotExist:
        return JsonResponse({'detail': 'News item not found'}, status=404)
    
    news_item.delete()
    return redirect('admin')