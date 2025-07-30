# vipps_auth/apps.py

from django.apps import AppConfig

class VippsAuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'vipps_auth'
    verbose_name = "Vipps Auth Provider"

    def ready(self):
        """
        This method is called by Django when the app is ready.
        We use it to explicitly register our provider with django-allauth.
        This is the most reliable way to ensure allauth knows about our custom provider.
        """
        try:
            from allauth.socialaccount import providers
            from .provider import VippsProvider
            # Apply compatibility monkey patch for OAuth2Client when the app is
            # fully loaded and Django's registry is ready.
            from . import patch_allauth_client

            patch_allauth_client()
            providers.registry.register(VippsProvider)
        except ImportError:
            # This try/except block is a safeguard for cases where allauth
            # might not be installed yet during certain management commands.
            pass