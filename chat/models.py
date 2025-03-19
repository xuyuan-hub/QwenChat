from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class AuthUser(AbstractUser):
    username = models.CharField(max_length=128,unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    is_active = models.IntegerField(default=1)
    pass

class Conversation(models.Model):
    id = models.UUIDField(primary_key=True)
    title = models.CharField(max_length=128)
    start_date = models.DateField(auto_now=True)
    user = models.ForeignKey(AuthUser,on_delete=models.CASCADE)


class ChatMessages(models.Model):
    role = models.CharField(max_length=64)
    content = models.TextField()
    start_time = models.DateTimeField(auto_now=True)
    conversation = models.ForeignKey(Conversation,on_delete=models.CASCADE)