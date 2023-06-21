"""configuration this app."""
from django.apps import AppConfig


class WebConfig(AppConfig):
    """app configuration class"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'web'
