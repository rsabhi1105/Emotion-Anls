from django.db import models

from accounts.models import CustomUser


# Create your models here.

class UserEmotion(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    speaker = models.CharField(max_length=255)
    analysis_date = models.DateTimeField()
    happiness = models.FloatField()
    sadness = models.FloatField()
    anger = models.FloatField()
    fear = models.FloatField()
    surprise = models.FloatField()
    neutral = models.FloatField()
        # improvement = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username
