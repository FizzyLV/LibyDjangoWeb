from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from account.models import Account 
from authTokenHandler.models import create_token

def register(request):
    return render(request, 'account/register.html')


@csrf_exempt
def token_login(request):
    if request.method != 'POST':
        return JsonResponse({'detail': 'Method not allowed'}, status=405)

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'detail': 'Invalid JSON'}, status=400)

    email = payload.get('email')
    password = payload.get('password')
    if not email or not password:
        return JsonResponse({'detail': 'Email and password required'}, status=400)

    try:
        account = Account.objects.get(email=email)  # ✅ Search Account table
    except Account.DoesNotExist:
        return JsonResponse({'detail': 'Invalid credentials'}, status=401)

    if account.password != password:  # ✅ Direct string comparison (no hashing)
        return JsonResponse({'detail': 'Invalid credentials'}, status=401)

    token = create_token(account)  # ✅ Pass the account object
    return JsonResponse({'token': token,
                         'firstName': account.firstName,
                         'lastName': account.lastName,
                        })