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
    


def create_token(Account):
    token = secrets.token_urlsafe(48)
    tokenRecord = AuthToken.objects.create (
        user=Account,
        token=token,
        expires_at=timezone.now() + timedelta(days=30)
    )

    return token