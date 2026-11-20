from api_client import ApiClient


def authenticate(username, password, api_client=None):
    """Authenticate against the local backend and return the account."""
    client = api_client or ApiClient()
    return client.login(username, password)
