from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
User = get_user_model()

class News(models.Model):
    title = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    published_relative_time = models.CharField(max_length=300, null=True)
    published_datetime = models.DateTimeField(blank=True,null=True)
    image = models.CharField(max_length=500)
    badge_status = models.CharField(max_length=50, blank=True, null=True,  choices=[
        ('Negative', 'Negative'),
        ('Positive', 'Positive')
    ])


    def __str__(self):
        return self.title

class Reaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    news = models.ForeignKey(News, on_delete=models.CASCADE)
    love = models.BooleanField(default=False)  # True if user loves/likes the news
    comment = models.TextField(blank=True, null=True)  # Optional comment by user
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp of reaction

    class Meta:
        unique_together = ('user', 'news')  # Prevent duplicate reactions per user per news

    def __str__(self):
        return f"{self.user.email} - {self.news.title} (Love: {self.love})"