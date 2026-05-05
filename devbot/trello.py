from dataclasses import dataclass
from typing import Any

import aiohttp

from devbot.config import TrelloSettings


TRELLO_CARDS_URL = "https://api.trello.com/1/cards"


class TrelloError(Exception):
    """Raised when Trello rejects or fails a request."""


@dataclass(frozen=True)
class TrelloCard:
    id: str
    name: str
    url: str


class TrelloClient:
    def __init__(self, settings: TrelloSettings) -> None:
        self.settings = settings

    async def create_card(self, name: str, description: str = "") -> TrelloCard:
        payload = {
            "key": self.settings.api_key,
            "token": self.settings.token,
            "idList": self.settings.list_id,
            "name": name,
            "desc": description,
            "pos": "top",
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(TRELLO_CARDS_URL, json=payload) as response:
                data = await self._read_response(response)

        return TrelloCard(
            id=data["id"],
            name=data["name"],
            url=data.get("url") or data.get("shortUrl", ""),
        )

    async def _read_response(self, response: aiohttp.ClientResponse) -> dict[str, Any]:
        if 200 <= response.status < 300:
            return await response.json()

        message = await response.text()
        raise TrelloError(f"{response.status} - {message}")
