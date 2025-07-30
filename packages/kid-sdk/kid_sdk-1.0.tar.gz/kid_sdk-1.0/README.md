
# KidOAuth2Client SDK

KID SDK provides an easy way to interact with OAuth2 and JWT services using `authlib`.

## Installation

To install the SDK, use pip:

```bash
pip install kid_sdk
```

## Usage

### KidOAuth2Client

#### Initialize the Client

```python
from kid_sdk.client import KidOAuth2Client

client_id = "your_client_id"
client_secret = "your_client_secret"
redirect_uri = "your_redirect_uri"
scope = "your_scope"

client = KidOAuth2Client(client_id, client_secret, redirect_uri, scope)
```

#### Get Authorization URL

```python
auth_url = client.get_authorization_url()
print(f"Visit this URL to authorize: {auth_url}")
```

#### Fetch Access Token

```python
code = "authorization_code_returned_by_provider"
access_token = client.fetch_token(code)
print(f"Access Token: {access_token}")
```

#### Get User Data

```python
user_data = client.get_user_data()
print(f"User Data: {user_data}")
```

### KidJWTClient

#### Parse JWT Token

```python
from kid_sdk.client import KidJWTClient

jwt_client = KidJWTClient()
encoded_jwt = "your_encoded_jwt"
key = "your_key"

claims = jwt_client.parse_jwt(encoded_jwt, key)
if claims:
    print(f"Claims: {claims}")
else:
    print("Failed to parse JWT")
```

## Logging

To enable logging, configure the logging module in your application:

```python
import logging

logging.basicConfig(level=logging.INFO)
```

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
