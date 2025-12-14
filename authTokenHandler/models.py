import secrets
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from account.models import Account

class AuthToken(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        ordering = ['-created_at']
    def is_valid(self):
        return self.expires_at > timezone.now()
    
    def __str__(self):
        return f"{self.user.username} - {self.token[:10]}..."
    


def createToken(Account):
    token = secrets.token_urlsafe(48)
    AuthToken.objects.create (
        user=Account,
        token=token,
        expires_at=timezone.now() + timedelta(days=30)
    )

    return token


def revokeToken(token):
    try:
        tokenRecord = AuthToken.objects.get(token=token)
        tokenRecord.delete()
        return True
    except AuthToken.DoesNotExist:
        return False
    
def isTokenValid(token):
    try:
        tokenRecord = AuthToken.objects.get(token=token)
        return tokenRecord.is_valid()
    except AuthToken.DoesNotExist:
        return False
    

def getUserByToken(token):
    try:
        tokenRecord = AuthToken.objects.get(token=token)
        if tokenRecord.is_valid():
            return tokenRecord.user
        else:
            return None
    except AuthToken.DoesNotExist:
        return None