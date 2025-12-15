from django.urls import reverse

def navbar_context(request):
    # Base nav items for everyone
    nav_items = []
    
    # Add admin-only items
    if request.session.get('isAdmin'):
        nav_items.extend([
            {'label': 'Admin Panel', 'url': reverse('admin')},
        ])
        nav_items.append({'label': 'Logout', 'url': reverse('logout')})
    
    return {
        'NavsiteName': 'LBY',
        'NavItems': nav_items,
        'Navis_admin': request.session.get('isAdmin', False),
        'Navcurrent_path': request.path,  
    }