# vipps_auth/settings.py
from django.conf import settings

# Define a single dictionary for all our settings for clean namespace in the project's settings.
USER_SETTINGS = getattr(settings, "VIPPS_AUTH_SETTINGS", {})

# Define the defaults for our package.
DEFAULTS = {
    "BASE_URL": "https://apitest.vipps.no",
    "SCOPES": [
        "openid",
        "name",
        "email",
        "phoneNumber",
    ],
    "EMAIL_VERIFIED_REQUIRED": True,
}

class VippsAuthSettings:
    """
    A settings object that allows our app's settings to be accessed as
    attributes. For example: `vipps_auth_settings.BASE_URL`.
    """
    def __init__(self, user_settings=None, defaults=None):
        # THE FIX IS HERE: We now always initialize self._user_settings.
        # This prevents the recursion error.
        self._user_settings = user_settings or {}
        self.defaults = defaults or {}

    def __getattr__(self, attr):
        if attr in self._user_settings:
            return self._user_settings[attr]
        if attr in self.defaults:
            return self.defaults[attr]
        raise AttributeError(f"Invalid Vipps Auth setting: '{attr}'")

# Instantiate the settings object that the rest of our package will use.
vipps_auth_settings = VippsAuthSettings(USER_SETTINGS, DEFAULTS)