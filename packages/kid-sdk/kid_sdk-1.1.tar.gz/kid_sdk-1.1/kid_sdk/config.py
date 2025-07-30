import os

DEBUG = False

INSTALLED_APPS = [
    "kid_sdk.kid_profile",
]

DATABASES = {
    db: {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": db,
        "USER": os.environ.get(f"{db.upper()}_POSTGRES_USER", None),
        "PASSWORD": os.environ.get(f"{db.upper()}_POSTGRES_PASSWORD", None),
        "HOST": os.environ.get(f"{db.upper()}_POSTGRES_HOST", None),
        "PORT": os.environ.get(f"{db.upper()}_POSTGRES_PORT", None),
        "ATOMIC_REQUESTS": False,
    }
    for db in ["domestic", "international"]
}
DATABASES["default"] = {
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": "profile",
}

DATABASE_ROUTERS = [
    "kid_sdk.kid_profile.routers.ProfileRouter",
]


# General
TEST_DOMAIN = "https://dev-smartid.zonesmart.ru"
DOMAIN = "https://id.kokocgroup.ru"

AUTHORIZATION_URL = "{domain}"
TOKEN_ISSUE_URL = "{domain}/api/oauth2/issue/"
GET_USER_DATA_URL = "{domain}/api/user/auth_data/"

DEFAULT_SCOPE = "smart_id first_name last_name email phone roles"
