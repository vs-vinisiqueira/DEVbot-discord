import json
from dataclasses import dataclass
from typing import Any

import aiohttp

from devbot.config import OpenAISettings


OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"


class OpenAIActionError(Exception):
    """Raised when OpenAI cannot return a usable action."""


@dataclass(frozen=True)
class AIAction:
    action: str
    channel: str
    message: str
    channel_name: str
    task_title: str
    reason: str


ACTION_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "action": {
            "type": "string",
            "enum": [
                "send_message",
                "pin_last_message",
                "create_text_channel",
                "create_trello_task",
                "unknown",
            ],
        },
        "channel": {"type": "string"},
        "message": {"type": "string"},
        "channel_name": {"type": "string"},
        "task_title": {"type": "string"},
        "reason": {"type": "string"},
    },
    "required": [
        "action",
        "channel",
        "message",
        "channel_name",
        "task_title",
        "reason",
    ],
}


SYSTEM_PROMPT = """
Voce interpreta pedidos em portugues feitos a um bot de Discord do projeto MeuSiteJa.
Retorne somente uma acao JSON valida conforme o schema.

Acoes permitidas:
- send_message: enviar uma mensagem em um canal de texto existente.
- pin_last_message: fixar a ultima mensagem valida do canal atual ou de um canal informado.
- create_text_channel: criar um canal de texto simples.
- create_trello_task: criar uma tarefa no Trello.
- unknown: pedido pouco claro, fora do escopo ou bloqueado.

Regras:
- Nao execute nada; apenas descreva a acao estruturada.
- Use strings vazias para campos que nao se aplicam.
- Para send_message, preencha channel e message.
- Para pin_last_message, preencha channel somente se o usuario informar um canal.
- Para create_text_channel, preencha channel_name.
- Para create_trello_task, preencha task_title.
- Se o pedido envolver banir, expulsar, apagar canais, apagar mensagens em massa,
  alterar permissoes, alterar cargos, @everyone, @here, conteudo ofensivo ou abusivo,
  tokens, secrets ou variaveis de ambiente, retorne action unknown e explique em reason.
- Se faltar informacao essencial, retorne action unknown.
"""


class OpenAIActionClient:
    def __init__(self, settings: OpenAISettings) -> None:
        self.settings = settings

    async def interpret(self, request_text: str) -> AIAction:
        if not self.settings.is_configured:
            raise OpenAIActionError(
                "OpenAI API key ausente. Defina OPENAI_API_KEY no arquivo .env."
            )

        payload = {
            "model": self.settings.model,
            "input": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": request_text},
            ],
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "discord_bot_action",
                    "strict": True,
                    "schema": ACTION_SCHEMA,
                }
            },
        }

        headers = {
            "Authorization": f"Bearer {self.settings.api_key}",
            "Content-Type": "application/json",
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                OPENAI_RESPONSES_URL,
                headers=headers,
                json=payload,
            ) as response:
                data = await self._read_response(response)

        return self._parse_action(data)

    async def _read_response(self, response: aiohttp.ClientResponse) -> dict[str, Any]:
        if 200 <= response.status < 300:
            return await response.json()

        message = await response.text()
        raise OpenAIActionError(f"Erro na OpenAI API: {response.status} - {message}")

    def _parse_action(self, data: dict[str, Any]) -> AIAction:
        output_text = data.get("output_text") or self._extract_output_text(data)

        if not output_text:
            raise OpenAIActionError("A OpenAI API nao retornou uma acao.")

        try:
            raw_action = json.loads(output_text)
        except json.JSONDecodeError as error:
            raise OpenAIActionError("JSON invalido retornado pela IA.") from error

        return self._validate_action(raw_action)

    def _extract_output_text(self, data: dict[str, Any]) -> str:
        parts: list[str] = []

        for item in data.get("output", []):
            for content in item.get("content", []):
                if content.get("type") == "output_text":
                    parts.append(content.get("text", ""))

        return "".join(parts)

    def _validate_action(self, raw_action: Any) -> AIAction:
        if not isinstance(raw_action, dict):
            raise OpenAIActionError("Resposta da IA nao esta no formato esperado.")

        valid_actions = {
            "send_message",
            "pin_last_message",
            "create_text_channel",
            "create_trello_task",
            "unknown",
        }
        action = raw_action.get("action")

        if action not in valid_actions:
            raise OpenAIActionError("A IA retornou uma acao nao permitida.")

        values = {
            "action": action,
            "channel": raw_action.get("channel", ""),
            "message": raw_action.get("message", ""),
            "channel_name": raw_action.get("channel_name", ""),
            "task_title": raw_action.get("task_title", ""),
            "reason": raw_action.get("reason", ""),
        }

        if not all(isinstance(value, str) for value in values.values()):
            raise OpenAIActionError("A IA retornou campos em formato invalido.")

        return AIAction(**values)
