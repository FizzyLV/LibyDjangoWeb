from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import check_password, make_password
import json
from account.models import Account 
from authTokenHandler.models import createToken, revokeToken, getUserByToken


@csrf_exempt
def token_login(request):
    if request.method != 'POST':
        return JsonResponse({'detail': 'Method not allowed'}, status=405)

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'detail': 'Invalid JSON'}, status=400)

    email = payload.get('email', '').strip()
    password = payload.get('password', '')
    
    if not email or not password:
        return JsonResponse({'detail': 'Email and password required'}, status=400)

    try:
        account = Account.objects.get(email=email)  
    except Account.DoesNotExist:
        return JsonResponse({'detail': 'Invalid credentials'}, status=401)

    if not check_password(password, account.password):
        return JsonResponse({'detail': 'Invalid credentials'}, status=401)

    token = createToken(account)
    
    # Debug: Print the isAdmin value
    print(f"DEBUG: User {account.email} isAdmin: {account.isAdmin}")
    
    return JsonResponse({
        'token': token,
        'firstName': account.firstName,
        'lastName': account.lastName,
        'isAdmin': account.isAdmin
    }, status=200)

@csrf_exempt
def token_logout(request):
    if request.method != 'POST':
        return JsonResponse({'detail': 'Method not allowed'}, status=405)
    token = request.headers.get('authorization')
    if not token:
        return  JsonResponse({'detail': 'Token required'}, status=400)
    revokeToken(token)
    return JsonResponse({'detail': 'Logged out successfully'}, status=200)


@csrf_exempt
def tokenDeleteAccount(request):
    if request.method != 'POST':
        return JsonResponse({'detail': 'Method not allowed'}, status=405)
    token = request.headers.get('authorization')
    if not token:
        return  JsonResponse({'detail': 'Token required'}, status=400)
    getUserByToken(token).delete()
    return JsonResponse({'detail': 'Deleted account successfully'}, status=200)

@csrf_exempt
def tokenRegister(request):
    if request.method != 'POST':
        return JsonResponse({'detail': 'Method not allowed'}, status=405)

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'detail': 'Invalid JSON'}, status=400)

    email = payload.get('email', '').strip()
    firstName = payload.get('firstName', '').strip()
    lastName = payload.get('lastName', '').strip()
    password = payload.get('password', '')

    # Debug (optional)
    print(email, firstName, lastName, password)

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

    # Create account
    account = Account.objects.create(
        email=email,
        firstName=firstName,
        lastName=lastName,
        password=make_password(password),
        isAdmin=False
    )

    # Generate token
    token = createToken(account)

    return JsonResponse(
        {
            'token': token,
            'firstName': account.firstName,
            'lastName': account.lastName,
            'isAdmin': account.isAdmin
        },
        status=201,
        json_dumps_params={'ensure_ascii': False}
    )

@csrf_exempt
def tokenVerify(request):
    if request.method != 'POST':
        return JsonResponse({'detail': 'Method not allowed'}, status=405)
    
    token = request.headers.get('authorization')
    if not token:
        return JsonResponse({'detail': 'Token required'}, status=400)
    
    user = getUserByToken(token)
    if not user:
        return JsonResponse({'detail': 'Invalid or expired token'}, status=401)
    
    return JsonResponse({
        'firstName': user.firstName,
        'lastName': user.lastName,
        'email': user.email,
        'isAdmin': user.isAdmin
    }, status=200)