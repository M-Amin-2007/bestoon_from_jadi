"""database models"""
from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Expense(models.Model):
    """model expense"""
    date = models.DateTimeField()
    text = models.CharField(max_length=200)
    amount = models.BigIntegerField()
    edit_mod = models.BooleanField(default=False)
    this_user = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.amount} in {self.date} for {self.this_user}"


class Income(models.Model):
    """model expense"""
    date = models.DateTimeField()
    text = models.CharField(max_length=200)
    amount = models.BigIntegerField()
    edit_mod = models.BooleanField(default=False)
    this_user = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.amount} in {self.date} for {self.this_user}--{self.edit_mod}"


class PasswordResetCodes(models.Model):
    """save user password and information"""
    code = models.CharField(max_length=32)
    date = models.DateTimeField()
    email = models.EmailField()
    user_name = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    def __str__(self):
        return f"{self.user_name}"
