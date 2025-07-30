import os
from jose import jwt
from jwt import PyJWKClient
import os

KEYCLOAK_URL = os.getenv("KEYCLOAK_URL")
REALM = os.getenv('REALM')
CLIENT_ID = os.getenv('CLIENT_ID')
ISSUER = f"{KEYCLOAK_URL}/realms/{REALM}"
AUDIENCE = os.getenv('AUDIENCE','account')  # as per your token
import requests

class KeycloakOnlineDecoder:
    def __init__(self):
        print("ctor")


    def can_execute(self, verify_mode) -> bool:
        """
        Check if execution is permitted.
        """
        return verify_mode == "ONLINE"

    def execute(self, token):
        url = f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/token/introspect"
        SHARED_SECRET = os.getenv('SHARED_SECRET')

        # 📤 Introspect request
        response = requests.post(
            url,
            data={'token': token},
            auth=(CLIENT_ID, SHARED_SECRET),
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )

        # 📥 Parse the response
        decoded_token = response.json()
        return decoded_token