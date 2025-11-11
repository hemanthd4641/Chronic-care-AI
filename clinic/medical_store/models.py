from django.db import models
from django.contrib.auth.models import User

class Medicine(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=100)
    category = models.CharField(max_length=100, default='General')
    manufacturer = models.CharField(max_length=200, blank=True, null=True)
    is_available = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def is_in_stock(self):
        return self.stock_quantity > 0 and self.is_available


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        unique_together = ['user', 'medicine']

    def get_total(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.user.username} - {self.medicine.name} x{self.quantity}"
