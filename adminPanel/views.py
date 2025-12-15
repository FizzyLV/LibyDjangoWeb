from django.shortcuts import render
from account.decorators import login_required
from adminPanel.decorators import admin_required
from News.models import newsItems
from django.shortcuts import redirect

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


