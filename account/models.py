from django.db import models
from django.core.validators import RegexValidator

name_validator = RegexValidator(
    regex=r'^[^\W\d_]+$',
    message='No symbols or spaces permitted.'
)




class Account(models.Model):
    firstName = models.CharField(max_length=20, validators=[name_validator])
    lastName = models.CharField(max_length=20, validators=[name_validator])
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=24)
    createdAt = models.DateTimeField(auto_now_add=True)
    isAdmin = models.BooleanField(default=False)
