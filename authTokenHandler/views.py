from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import check_password
import json
from account.models import Account 
from authTokenHandler.models import createToken, revokeToken

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
    
    return JsonResponse({
        'token': token,
        'firstName': account.firstName,
        'lastName': account.lastName
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