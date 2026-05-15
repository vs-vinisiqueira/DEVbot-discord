import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class TrelloSettings:
    api_key: str | None
    token: str | None
    list_id: str | None

    @property
    def is_configured(self) -> bool:
        return all([self.api_key, self.token, self.list_id])


@dataclass(frozen=True)
class OpenAISettings:
    api_key: str | None
    model: str

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)


@dataclass(frozen=True)
class Settings:
    discord_token: str
    command_prefix: str
    trello: TrelloSettings
    openai: OpenAISettings


def load_settings() -> Settings:
    load_dotenv()

    discord_token = os.getenv("DISCORD_TOKEN")
    if not discord_token:
        raise ValueError("Token do Discord não encontrado. Verifique o arquivo .env.")

    return Settings(
        discord_token=discord_token,
        command_prefix=os.getenv("COMMAND_PREFIX", "!"),
        trello=TrelloSettings(
            api_key=os.getenv("TRELLO_API_KEY"),
            token=os.getenv("TRELLO_TOKEN"),
            list_id=os.getenv("TRELLO_LIST_ID"),
        ),
        openai=OpenAISettings(
            api_key=os.getenv("OPENAI_API_KEY"),
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        ),
    )
