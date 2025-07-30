"""Vipps Auth package initialization."""

def patch_allauth_client() -> None:
    """Monkey patch ``django-allauth``'s ``OAuth2Client`` for older callers."""

    from allauth.socialaccount.providers.oauth2 import client as oauth2_client

    class _CompatOAuth2Client(oauth2_client.OAuth2Client):
        """Compatibility wrapper for ``OAuth2Client`` with a ``scope`` arg."""

        def __init__(
            self,
            request,
            consumer_key,
            consumer_secret,
            access_token_method,
            access_token_url,
            callback_url,
            scope=None,
            *,
            scope_delimiter=" ",
            headers=None,
            basic_auth=False,
        ) -> None:
            # ``scope`` is ignored but retained for backward compatibility.
            super().__init__(
                request,
                consumer_key,
                consumer_secret,
                access_token_method,
                access_token_url,
                callback_url,
                scope_delimiter=scope_delimiter,
                headers=headers,
                basic_auth=basic_auth,
            )

    oauth2_client.OAuth2Client = _CompatOAuth2Client

