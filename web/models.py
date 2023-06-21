"""database models"""
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Token(models.Model):
    """token for each user to be secret."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token_m = models.CharField(max_length=50)
    def __str__(self):
        return f"{self.user} token"


class Expense(models.Model):
    """model expense"""
    date = models.DateTimeField()
    text = models.CharField(max_length=200)
    amount = models.BigIntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.amount} in {self.date}"


class Income(models.Model):
    """model expense"""
    date = models.DateTimeField()
    text = models.CharField(max_length=200)
    amount = models.BigIntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.amount} in {self.date}"
