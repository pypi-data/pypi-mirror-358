# vipps_auth/provider.py

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider
from allauth.account.adapter import get_adapter
from .settings import vipps_auth_settings

class VippsAccount(ProviderAccount):
    def to_str(self):
        return self.account.extra_data.get('name', super().to_str())

class VippsProvider(OAuth2Provider):
    id = 'vipps'
    name = 'Vipps'
    account_class = VippsAccount

    # THE FIX, PART 1:
    # The provider itself must define the endpoint URLs as class attributes.
    # This makes it a self-contained definition for the Vipps service.
    access_token_url = f"{vipps_auth_settings.BASE_URL}/access-management-1.0/access/oauth2/token"
    authorize_url = f"{vipps_auth_settings.BASE_URL}/access-management-1.0/access/oauth2/auth"
    profile_url = f"{vipps_auth_settings.BASE_URL}/vipps-userinfo-api/userinfo"

    def get_default_scope(self):
        return vipps_auth_settings.SCOPES

    def extract_uid(self, data):
        uid = data.get('sub')
        if not uid:
            get_adapter().error("Vipps user data did not contain a 'sub' identifier.")
        return str(uid)

    def extract_common_fields(self, data):
        return {
            'email': data.get('email'),
            'first_name': data.get('given_name'),
            'last_name': data.get('family_name'),
        }
        
    def extract_extra_data(self, data):
        return data

    def sociallogin_from_response(self, request, response):
        adapter = get_adapter()
        if vipps_auth_settings.EMAIL_VERIFIED_REQUIRED:
            email_verified = response.get('email_verified', False)
            if not email_verified:
                adapter.error("Login cancelled: Email from Vipps is not verified.")
        return super().sociallogin_from_response(request, response)