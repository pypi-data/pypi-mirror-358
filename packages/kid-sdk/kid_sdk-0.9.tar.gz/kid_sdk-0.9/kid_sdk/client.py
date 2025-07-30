import logging

import pendulum
import requests

from authlib.integrations.requests_client import OAuth2Session
from authlib.jose import jwt
from authlib.jose.errors import (
    JoseError,
    DecodeError,
    BadSignatureError,
    ExpiredTokenError,
    InvalidClaimError,
)
from requests.exceptions import HTTPError

from .config import (
    AUTHORIZATION_URL,
    DEFAULT_SCOPE,
    DOMAIN,
    GET_USER_DATA_URL,
    TEST_DOMAIN,
    TOKEN_ISSUE_URL,
)
from .utils import validate_token


class KidOAuth2Client:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        scope: str = DEFAULT_SCOPE,
        test: bool = False,
    ):
        """
        Initializes the OAuth2 client.

        :param client_id: Client identifier
        :param client_secret: Client secret
        :param redirect_uri: Redirect URI
        :param scope: A space-separated string of OAuth2 scopes defining the level of access
                      the client is requesting. Scopes control the permissions granted by the
                      authorization server, such as access to user profile, email, or other resources.
                      Example: "smart_id first_name last_name email phone"
        :param test: Boolean indicating whether to use the test domain
        """
        self.redirect_uri = redirect_uri
        self.session = OAuth2Session(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=scope,
        )
        self.token = None
        self.token_expires_at = None
        self.domain = TEST_DOMAIN if test else DOMAIN
        self.authorization_url = AUTHORIZATION_URL.format(domain=self.domain)
        self.token_issue_url = TOKEN_ISSUE_URL.format(domain=self.domain)
        self.get_user_data_url = GET_USER_DATA_URL.format(domain=self.domain)

    @property
    def token_is_expired(self) -> bool:
        if self.token_expires_at is None:
            return True
        return pendulum.now("UTC").timestamp() >= self.token_expires_at

    def get_authorization_url(self) -> str:
        """
        Creates an authorization URL.

        :return: Authorization URL
        """
        return self.session.create_authorization_url(self.authorization_url, redirect_uri=self.redirect_uri)[0]

    def fetch_token(self, code: str) -> str:
        """
        Fetches the access token.

        :param code: Authorization code
        :return: Access token
        :raises Exception: If there is an error fetching the token
        """
        try:
            self.token = self.session.fetch_token(self.token_issue_url, code=code)
        except Exception as e:
            logging.error(f"Error fetching token: {e}")
            raise

        self.token_expires_at = self.token["expires_at"]
        return self.token["access_token"]

    @validate_token
    def get_user_data(self) -> dict:
        """
        Retrieves user data using the token.

        :return: Dictionary containing user data
        :raises HTTPError: If the request fails
        """
        self.session.token = self.token

        try:
            response = self.session.get(self.get_user_data_url)
            response.raise_for_status()
        except HTTPError as http_err:
            logging.error(f"HTTP error occurred: {http_err}")
            raise
        except Exception as err:
            logging.error(f"Error occurred: {err}")
            raise

        return response.json()


class KidJWTClientException(Exception):
    pass


class KidJWTClient:
    @staticmethod
    def parse_jwt(encoded_jwt: str, key: str) -> dict:
        """
        Parses a JWT token.

        :param encoded_jwt: Encoded JWT token
        :param key: Key for decoding
        :return: Dictionary containing claims or None if an error occurs
        """
        try:
            claims = jwt.decode(encoded_jwt, key)
            claims.validate()
        except DecodeError as e:
            message = f"Failed to decode JWT: {e}"
            logging.error(message)
            raise KidJWTClientException(message)
        except BadSignatureError as e:
            message = f"Invalid signature: {e}"
            logging.error(message)
            raise KidJWTClientException(message)
        except ExpiredTokenError as e:
            message = f"Token has expired: {e}"
            logging.error(message)
            raise KidJWTClientException(message)
        except InvalidClaimError as e:
            message = f"Invalid claim: {e}"
            logging.error(message)
            raise KidJWTClientException(message)
        except JoseError as e:
            message = f"Failed to decode JWT: {e}"
            logging.error(message)
            raise KidJWTClientException(message)

        if not isinstance(claims, dict):
            logging.error("Claims data is not a dictionary")
            raise TypeError("Claims data is not a dictionary")

        return claims

    @classmethod
    def mark_user_as_transferred(cls, smart_id: str, site_id: str, key: str, test: bool = False) -> dict:
        """
        Отправка данных пользователя в Kokoc ID
        """
        data = {
            "site": site_id,
            "token": jwt.encode(header={"alg": "HS256"}, payload={"smart_id": smart_id}, key=key).decode(),
        }
        url = TEST_DOMAIN if test else DOMAIN
        response = requests.post(url + "/api/user/mark_user_as_transferred/", json=data)
        if response.status_code != 201:
            return response.json()
