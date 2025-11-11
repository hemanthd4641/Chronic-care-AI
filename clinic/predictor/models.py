from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class PredictionHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    disease_type = models.CharField(max_length=50)
    prediction_result = models.IntegerField()  # 0 or 1
    confidence = models.FloatField(null=True, blank=True)
    input_data = models.JSONField()  # Store all the form data
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Prediction Histories"
    
    def __str__(self):
        return f"{self.user.username} - {self.disease_type} - {self.get_result_display()}"
    
    def get_result_display(self):
        return "High Risk" if self.prediction_result == 1 else "Low Risk"
    
    def get_disease_display(self):
        disease_names = {
            'heart': 'Heart Disease',
            'hypertension': 'Hypertension',
            'diabetes': 'Diabetes',
            'kidney': 'Kidney Disease'
        }
        return disease_names.get(self.disease_type, self.disease_type.title())
