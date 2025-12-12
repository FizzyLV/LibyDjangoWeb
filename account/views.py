from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password, check_password
from account.models import Account 
def register(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        firstName = request.POST.get('firstName', '').strip()
        lastName = request.POST.get('lastName', '').strip()
        password = request.POST.get('password', '')
        
        # Validation
        if not email:
            return JsonResponse({'detail': 'Email is required'}, status=400)
        if not firstName or not lastName:
            return JsonResponse({'detail': 'First name and last name are required'}, status=400)
        if not password:
            return JsonResponse({'detail': 'Password is required'}, status=400)
        if len(password) < 8:
            return JsonResponse({'detail': 'Password must be at least 8 characters long'}, status=400)
        if Account.objects.filter(email=email).exists():
            return JsonResponse({'detail': 'Email already in use'}, status=400)
        
        Account.objects.create(
            email=email,
            firstName=firstName,
            lastName=lastName,
            password=make_password(password)
        )
        
        return JsonResponse({'detail': 'Account created successfully'}, status=201)
    if request.session.get('is_authenticated'):
        return redirect('home')
    else:
         return render(request, 'account/register.html')

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        
        if not email or not password:
            return JsonResponse({'detail': 'Email and password are required'}, status=400)
        
        try:
            account = Account.objects.get(email=email)
        except Account.DoesNotExist:
            return JsonResponse({'detail': 'Invalid email or password'}, status=401)
        
        if not check_password(password, account.password):
            return JsonResponse({'detail': 'Invalid email or password'}, status=401)
        
        # Log the user in using Django's session framework
        request.session['userId'] = account.id
        request.session['isAuthenticated'] = True
        request.session['isAdmin'] = account.isAdmin
        
        return JsonResponse({
            'detail': 'Login successful',
            'firstName': account.firstName,
            'lastName': account.lastName,
            'isAdmin': account.isAdmin
        }, status=200)
    if request.session.get('isAuthenticated'):
        return redirect('home')
    else:
         return render(request, 'account/login.html')
    
def logout(request):
    request.session.flush()
    return redirect('login')