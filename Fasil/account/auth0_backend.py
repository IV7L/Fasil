import requests
from django.conf import settings
from django.contrib.auth import get_user_model

from account.models import CustomUser
User = get_user_model()

class Auth0Backend:
    def authenticate(self, request, token=None):
        if not token:
            return None

        # Validate the token and retrieve user information from Auth0
        user_info = self.validate_auth0_token(token)

        if not user_info:
            return None

        # Check if a user with the given email already exists in the Django database
        try:
            user = CustomUser.objects.get(email=user_info["email"])
        except CustomUser.DoesNotExist:
            user = CustomUser.objects.create (
                email=user_info["email"],
                username= user_info["name"],
                email_verified= user_info["email_verified"],
                is_staff= True,
            )
        
        return user

    def validate_auth0_token(self, token):
        # Use the Auth0 token to fetch user information
        auth0_domain = settings.AUTH0_DOMAIN
        auth0_api_url = f'https://{auth0_domain}/userinfo'
        headers = {'Authorization': f'Bearer {token["access_token"]}'}

        response = requests.request("GET", auth0_api_url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
