# Django Allauth Vipps Provider

[![PyPI version](https://badge.fury.io/py/django-allauth-vipps.svg)](https://pypi.org/project/django-allauth-vipps/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI/CD Tests](https://github.com/danpejobo/django-allauth-vipps/actions/workflows/ci.yml/badge.svg)](https://github.com/danpejobo/django-allauth-vipps/actions/workflows/ci.yml)

A complete `django-allauth` provider for Vipps Login, supporting both traditional web and modern API (`dj-rest-auth`) authentication flows.

This package provides a configurable, reusable Django app that allows users to sign in to your project using their Vipps account, making it easy to integrate Norway's most popular payment and identity solution.

## Features

-   Integrates seamlessly with `django-allauth`'s social account framework.
-   Supports API-first authentication flows via `dj-rest-auth` for use with SPAs (React, Vue, etc.) or mobile apps.
-   Configurable for both Vipps Test and Production environments.
-   Allows customization of requested scopes (e.g., name, email, phone number).
-   Fully tested and documented.

## 1. Installation & Setup

### Prerequisites

This package assumes you have a Django project with `django-allauth` already installed and configured. If not, please follow the [django-allauth installation guide](https://django-allauth.readthedocs.io/en/latest/installation/index.html) first.

### Step 1: Install the Package

Install using `pip` or your project's dependency manager.

```bash
pip install django-allauth-vipps
```
*(Or `poetry add django-allauth-vipps` if you use Poetry)*

### Step 2: Update Django Settings

Add `vipps_auth` to your `INSTALLED_APPS` in your Django `settings.py`. It must be placed after the standard `allauth` apps.

```python
# settings.py

INSTALLED_APPS = [
    # ... other apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # Required by allauth

    # Allauth apps
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    
    # Add the Vipps provider app
    'vipps_auth',
]

# Required by allauth
SITE_ID = 1

# Ensure you have authentication backends configured
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]
```

### Step 3: Run Database Migrations

Run migrations to ensure the `allauth` models are created in your database.

```bash
python manage.py migrate
```

### Step 4: Configure on Vipps Developer Portal

1.  Log in to the [Vipps MobilePay Developer Portal](https://portal.vippsmobilepay.com/).
2.  Navigate to the "Developer" section and select your profile.
3.  Add a new sale unit (`salgsenhet`) or use an existing one.
4.  Under the sale unit, go to the **"Logg inn med Vipps"** tab and get your credentials:
    * **Client ID**
    * **Client Secret**
5.  In the "Redirect URIs" section, add the URL that Vipps will redirect users back to after they log in. This is a critical step.
    * For **standard web flows**: `https://yourdomain.com/accounts/vipps/login/callback/`
    * For **API/SPA flows**: This should be the URL of your *frontend* application that handles the callback, e.g., `https://my-react-app.com/auth/callback/vipps`

### Step 5: Configure in Django Admin

1.  Start your Django server and log in to the admin panel.
2.  Go to **"Social applications"** and click **"Add social application"**.
3.  Fill out the form:
    * **Provider:** Choose **Vipps** from the dropdown.
    * **Name:** A descriptive name (e.g., "My Website Vipps Login").
    * **Client id:** Your Vipps `client_id` from the portal.
    * **Secret key:** Your Vipps `client_secret` from the portal.
    * **Sites:** Select your site and move it to the "Chosen sites" box.
4.  Save the application.

## 2. Usage

### For Traditional Django Websites

If you are using server-rendered templates, you can add a Vipps login button easily with the `provider_login_url` template tag.

**In your template (`login.html`):**

```html
{% load socialaccount %}

<h2>Login</h2>
<a href="{% provider_login_url 'vipps' %}">Log In with Vipps</a>
```
`django-allauth` will handle the entire redirect and callback flow automatically.

### For REST APIs (with `dj-rest-auth`)

This is the most common use case for modern frontends (React, Vue, mobile apps). The flow involves your frontend getting an authorization `code` from Vipps and exchanging it for a JWT token from your backend.

#### Step 1: Create the API Endpoint

In your project's `urls.py`, create a login view that uses the `VippsOAuth2Adapter`.

```python
# your_project/urls.py
from django.urls import path
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from vipps_auth.views import VippsOAuth2Adapter

# This view connects dj-rest-auth to our Vipps adapter
class VippsLoginAPI(SocialLoginView):
    adapter_class = VippsOAuth2Adapter
    client_class = OAuth2Client
    # This MUST match the redirect URI you set in the Vipps Portal for your frontend
    callback_url = "YOUR_FRONTEND_CALLBACK_URL" 

urlpatterns = [
    # ... your other urls
    path("api/v1/auth/vipps/", VippsLoginAPI.as_view(), name="vipps_login_api"),
]
```

#### Step 1.1: If step 1 fails

If for some reason step 1 fails, you can try to use basic auth.

```python
# your_project/urls.py
from django.urls import path
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from vipps_auth.views import VippsOAuth2Adapter

# 1. Create a custom client class that uses HTTP Basic auth when
#    exchanging the authorization code. In production Vipps expects the
#    `client_id` and `client_secret` to be provided via the
#    `Authorization` header, so we enable `basic_auth`.
class VippsBasicAuthClient(OAuth2Client):
    def __init__(self, *args, **kwargs):
        # Use HTTP Basic auth for the token request
        kwargs['basic_auth'] = True
        super().__init__(*args, **kwargs)

# This view connects dj-rest-auth to our Vipps adapter
class VippsLoginAPI(SocialLoginView):
    adapter_class = VippsOAuth2Adapter
    client_class = VippsBasicAuthClient
    # This MUST match the redirect URI you set in the Vipps Portal for your frontend
    callback_url = "YOUR_FRONTEND_CALLBACK_URL" 

urlpatterns = [
    # ... your other urls
    path("api/v1/auth/vipps/", VippsLoginAPI.as_view(), name="vipps_login_api"),
]
```

#### Step 2: The Frontend Flow

1.  **Redirect to Vipps:** Your frontend redirects the user to the Vipps authorization URL. You can get this URL from your provider's `get_authorize_url()` method or construct it manually.

2.  **Handle the Callback:** After the user logs in, Vipps redirects them to your `callback_url` (e.g., `https://my-react-app.com/auth/callback/vipps`) with a code in the query parameters:
    `?code=ABC-123...&state=...`

3.  **Exchange Code for JWT:** Your frontend grabs the `code` from the URL and sends it to your Django API endpoint.

    **Example using JavaScript `fetch`:**
    ```javascript
    async function exchangeCodeForToken(authCode) {
      try {
        const response = await fetch('https://yourdomain.com/api/v1/auth/vipps/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ code: authCode }),
        });
        
        if (!response.ok) {
          throw new Error('Failed to log in with Vipps');
        }

        const data = await response.json();
        // The data object now contains your JWTs
        // { "access": "...", "refresh": "..." }
        console.log(data); 
        // Save tokens to local storage and set user as logged in
      } catch (error) {
        console.error('Vipps login error:', error);
      }
    }
    ```

## 3. Advanced Configuration

You can customize the provider's behavior by adding a `VIPPS_AUTH_SETTINGS` dictionary to your project's `settings.py`.

**Example `settings.py`:**

```python
# settings.py

VIPPS_AUTH_SETTINGS = {
    # The base URL for the Vipps API.
    # Default: "https://apitest.vipps.no" (for testing)
    # For production, use: "https://api.vipps.no"
    "BASE_URL": "https://api.vipps.no",

    # The scopes (permissions) you request from the user.
    # Default: ["openid", "name", "email", "phoneNumber"]
    "SCOPES": [
        "openid",
        "name",
        "email",
    ],

    # If True, login will fail if Vipps reports the user's email is not verified.
    # Recommended to keep this as True for security.
    # Default: True
    "EMAIL_VERIFIED_REQUIRED": True,
}
```

## 4. Development & Testing

To work on this package locally:

1.  Clone the repository: `git clone https://github.com/danpejobo/django-allauth-vipps.git`
2.  Navigate to the directory: `cd django-allauth-vipps`
3.  Install all dependencies: `poetry install`
4.  Activate the virtual environment: `poetry shell`
5.  Run the test suite: `poetry run pytest`
