from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from rest_framework.authtoken.models import Token


# Create your views here.
def register(request):
    return render(request, 'account/register.html')


@csrf_exempt
def token_login(request):
    """API endpoint: POST JSON {"email": "...", "password": "..."}
    Returns 200 with {"token": "..."} on success or 400/401 with error message.
    """
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

    User = get_user_model()
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return JsonResponse({'detail': 'Invalid credentials'}, status=401)

    if not user.check_password(password):
        return JsonResponse({'detail': 'Invalid credentials'}, status=401)

    token, _ = Token.objects.get_or_create(user=user)
    return JsonResponse({'token': token.key})