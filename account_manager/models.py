"""define models to create database from those by django."""
from django.db import models

# Create your models here.

class AccountActivatingCodes(models.Model):
    """save user password and information to activate their account"""
    code = models.CharField(max_length=32)
    date = models.DateTimeField()
    email = models.EmailField()
    user_name = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    def __str__(self):
        return f"{self.user_name}"
