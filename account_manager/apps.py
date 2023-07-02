"""app config"""
from django.apps import AppConfig


class AccountManagerConfig(AppConfig):
    """configure this app on project level."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'account_manager'
