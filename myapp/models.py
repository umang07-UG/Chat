from django.db import models
from django.utils import timezone
# Create your models here.


class User(models.Model):
    name = models.CharField(max_length=100)
    email =models.EmailField()
    mobile = models.BigIntegerField()
    password = models.CharField(max_length=20)
    profile_image = models.ImageField(default="",upload_to="profile_img/")

    def __str__(self):
        return f"{self.name}"
    
class Chat(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user2')

    def __str__(self):
        return f"{self.user1} - {self.user2}"

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)