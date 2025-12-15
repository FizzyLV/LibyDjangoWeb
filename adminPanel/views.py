from django.shortcuts import render
from account.decorators import login_required
from adminPanel.decorators import admin_required
from News.models import newsItems
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from authTokenHandler.models import getUserByToken
from django.http import JsonResponse

# Create your views here.

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

@login_required
@admin_required
def editNews(request, id):
    try:
        news_item = newsItems.objects.get(id=id)
    except newsItems.DoesNotExist:
        return JsonResponse({'detail': 'News item not found'}, status=404)
    
    if request.method == 'POST':
        # Get the form data
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        image = request.FILES.get('image', None)
        
        # Validation
        if not title or not description:
            return JsonResponse({'detail': 'Title and description are required'}, status=400)
        
        # Update the news item
        news_item.title = title
        news_item.description = description
        
        # Only update image if a new one was uploaded
        if image:
            news_item.image = image
        
        news_item.save()
        
        # Redirect back to admin panel after successful edit
        return redirect('admin')
    
    # GET request - display the form
    edit_context = {
        'news_item': news_item,  # Changed to match template variable name
    }
    
    return render(request, 'editNews.html', edit_context)


@csrf_exempt
def editNewsToken(request, id): 
    if request.method != 'POST':
        return JsonResponse({'detail': 'Method not allowed'}, status=405)
    
    token = request.headers.get('authorization')
    if not token:
        return JsonResponse({'detail': 'Token required'}, status=400)
    
    user = getUserByToken(token)
    if not user:
        return JsonResponse({'detail': 'Invalid or expired token'}, status=401)
    
    if not user.isAdmin:
        return JsonResponse({'detail': 'Admin access required'}, status=403)
    
    # Get the news item
    try:
        news_item = newsItems.objects.get(id=id)
    except newsItems.DoesNotExist:
        return JsonResponse({'detail': 'News item not found'}, status=404)
    
    # Get data
    title = request.POST.get('title', '').strip()
    description = request.POST.get('description', '').strip()
    image = request.FILES.get('image', None)
    
    # Validation
    if not title or not description:
        return JsonResponse({'detail': 'Title and description are required'}, status=400)
    
    # Update news item
    news_item.title = title
    news_item.description = description
    
    if image:
        news_item.image = image
    
    news_item.save()
    
    return JsonResponse({'detail': 'News updated successfully'}, status=200)