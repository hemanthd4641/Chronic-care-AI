from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

class Chats(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created = models.DateTimeField(default=now, blank=True)
    
    def __str__(self):
        return self.message

class Report(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    CATEGORY_CHOICES = [
        ('academic', 'Academic Issue'),
        ('facility', 'Facility Issue'),
        ('food', 'Food & Dining'),
        ('accommodation', 'Accommodation'),
        ('health', 'Health & Safety'),
        ('other', 'Other'),
    ]
    
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    report_title = models.CharField(max_length=200, blank=True, null=True)
    report = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, blank=True, null=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='low')
    rating = models.IntegerField(choices=RATING_CHOICES, default=5)
    recived = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created']
    
    def __str__(self):
        return f"{self.user.username} - {self.report_title or f'Report #{self.id}'}"