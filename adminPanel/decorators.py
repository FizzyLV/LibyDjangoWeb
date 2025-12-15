from django.shortcuts import redirect
from functools import wraps

def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('isAdmin'):
            return redirect('admin/denied')
        return view_func(request, *args, **kwargs)
    return wrapper