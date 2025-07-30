from typing import Type, TypeVar
from aiohttp import ClientSession
from urllib.parse import urljoin

from python_swos_lite.endpoint import SwOSLiteEndpoint, readDataclass

T = TypeVar("T", bound=SwOSLiteEndpoint)

class Client:
    """Client to connect to the available endpoints"""
    host: str
    session: ClientSession

    def __init__(self, session: ClientSession, host: str):
        self.session = session
        self.host = host.rstrip("/") + "/"  # Make sure host ends with a single "/"

    async def fetch(self, cls: Type[T]) -> T:
        async with self.session.get(urljoin(self.host, cls.endpoint_path)) as response:
            response.raise_for_status()
            text = await response.text()
            return readDataclass(cls, text)
