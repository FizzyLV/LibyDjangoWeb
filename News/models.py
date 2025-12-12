from django.db import models
from account.models import Account

class newsItems(models.Model):
    author = models.ForeignKey(Account, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='news_images/')
    description = models.TextField()
    publishedAt = models.DateTimeField(auto_now_add=True)
