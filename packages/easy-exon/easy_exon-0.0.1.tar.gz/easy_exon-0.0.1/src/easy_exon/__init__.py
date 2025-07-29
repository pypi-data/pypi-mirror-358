import requests

from .client import BaseClient
from .resources.objects import ObjectsResource
from .exceptions import TokenError


BASE_URL = "https://exon.exonproject.ru/"


class MyApiClient(BaseClient):
    def __init__(self, base_url: str = BASE_URL, token: str = None):
        super().__init__(base_url, token)
        self.objects = ObjectsResource(self)


def get_token(username: str, password: str) -> str:
    resp = requests.post(
        f"https://exon.exonproject.ru/auth/realms/SpringBoot/protocol/openid-connect/token",
        data = {
            "grant_type": "password",
            "client_id":  "ExonReactApp",
            "username":   username,
            "password":   password,
            "scope":      "openid",
        },
        timeout = 10,
    )

    if not resp.ok:
        raise TokenError(resp.status_code, resp.text)
    return resp.json()["access_token"]
