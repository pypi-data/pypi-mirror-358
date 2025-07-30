# vipps_auth/views.py

from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)
from .provider import VippsProvider

class VippsOAuth2Adapter(OAuth2Adapter):
    provider_id = VippsProvider.id

    # THE FIX, PART 2:
    # The adapter must also have these attributes for dj-rest-auth to find.
    # We simply point them to the definitive URLs on our provider class.
    access_token_url = VippsProvider.access_token_url
    authorize_url = VippsProvider.authorize_url
    profile_url = VippsProvider.profile_url

    def complete_login(self, request, app, token, **kwargs):
        """Fetch user info from Vipps and return a populated SocialLogin."""
        import requests
        from allauth.socialaccount import providers

        headers = {
            "Authorization": f"Bearer {token.token}",
        }

        resp = requests.get(self.profile_url, headers=headers)
        resp.raise_for_status()
        extra_data = resp.json()
        provider_cls = providers.registry.get_class(self.provider_id)
        provider = provider_cls(request, app=app)
        return provider.sociallogin_from_response(request, extra_data)


# These standard views use our adapter and provider correctly.
vipps_login = OAuth2LoginView.adapter_view(VippsOAuth2Adapter)
vipps_callback = OAuth2CallbackView.adapter_view(VippsOAuth2Adapter)