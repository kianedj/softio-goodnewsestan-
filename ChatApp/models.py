from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings
# Create your models here.

class Chat(models.Model):
    sender = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name= 'sender')
    reciver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name= 'reciver')
    message = models.CharField(max_length=1200, null=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return self.message
    
    def get_absolute_url(self):
        return reverse('chat_detail', args=[str(self.id)])
    class Meta:
        ordering = ('timestamp',)


    
