import functools


def validate_token(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.token:
            raise Exception("Token is not available. Please fetch the token first.")
        if self.token_is_expired:
            raise Exception("Token has expired. Please fetch a new token.")
        return func(self, *args, **kwargs)

    return wrapper
