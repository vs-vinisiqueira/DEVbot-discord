import re

import discord
from discord.ext import commands

from devbot.config import OpenAISettings, TrelloSettings
from devbot.openai_client import AIAction, OpenAIActionClient, OpenAIActionError
from devbot.trello import TrelloClient, TrelloError


MESSAGE_ALLOWED_ROLES = {"Administrador", "Equipe"}
BLOCKED_CONTENT = (
    "@everyone",
    "@here",
    "DISCORD_TOKEN",
    "OPENAI_API_KEY",
    "TRELLO_API_KEY",
    "TRELLO_TOKEN",
    "TRELLO_LIST_ID",
)
ABUSIVE_TERMS = {
    "idiota",
    "burro",
    "inutil",
    "inútil",
    "otario",
    "otário",
    "lixo",
}


def register_ai_action_commands(
    bot: commands.Bot,
    openai_settings: OpenAISettings,
    trello_settings: TrelloSettings,
) -> None:
    openai_client = OpenAIActionClient(openai_settings)

    @bot.command(name="ia")
    async def ai_action(ctx: commands.Context, *, request_text: str) -> None:
        if ctx.guild is None:
            await ctx.send("Esse comando só pode ser usado dentro de um servidor.")
            return

        try:
            action = await openai_client.interpret(request_text)
        except OpenAIActionError as error:
            await ctx.send(str(error))
            return

        try:
            await execute_action(ctx, action, request_text, trello_settings)
        except discord.Forbidden:
            await ctx.send(
                "Não tenho permissão suficiente no Discord para executar essa ação."
            )
        except discord.HTTPException as error:
            await ctx.send(f"O Discord recusou a ação: {error}")

    @ai_action.error
    async def ai_action_error(
        ctx: commands.Context,
        error: commands.CommandError,
    ) -> None:
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Use: !ia enviar no canal arquivos: "mensagem"')
        else:
            await ctx.send(f"Ocorreu um erro: {error}")


async def execute_action(
    ctx: commands.Context,
    action: AIAction,
    request_text: str,
    trello_settings: TrelloSettings,
) -> None:
    if action.action == "unknown":
        reason = action.reason or "Não entendi uma ação permitida nesse pedido."
        await ctx.send(f"Não executei a ação: {reason}")
        return

    if is_dangerous_request(request_text):
        await ctx.send("Não executei a ação porque o pedido contém algo bloqueado.")
        return

    if action.action == "send_message":
        await send_message_action(ctx, action)
        return

    if action.action == "pin_last_message":
        await pin_last_message_action(ctx, action)
        return

    if action.action == "create_text_channel":
        await create_text_channel_action(ctx, action)
        return

    if action.action == "create_trello_task":
        await create_trello_task_action(ctx, action, trello_settings)
        return

    await ctx.send("Não executei a ação porque ela não é permitida.")


async def send_message_action(ctx: commands.Context, action: AIAction) -> None:
    if not can_send_message(ctx):
        await ctx.send(
            "Você precisa ser administrador ou ter o cargo Equipe para enviar mensagens pela IA."
        )
        return

    if not action.channel or not action.message:
        await ctx.send("Não encontrei o canal ou a mensagem para enviar.")
        return

    if has_blocked_content(action.message) or looks_abusive(action.message):
        await ctx.send("Não executei a ação porque a mensagem contém conteúdo bloqueado.")
        return

    channel = find_text_channel(ctx.guild, action.channel)
    if channel is None:
        await ctx.send(f"Canal não encontrado: #{clean_channel_name(action.channel)}")
        return

    permissions = channel.permissions_for(ctx.guild.me)
    if not permissions.send_messages:
        await ctx.send(f"Não tenho permissão para enviar mensagens em #{channel.name}.")
        return

    await channel.send(action.message, allowed_mentions=discord.AllowedMentions.none())
    await ctx.send(f"Mensagem enviada em #{channel.name}.")


async def pin_last_message_action(ctx: commands.Context, action: AIAction) -> None:
    if not is_admin(ctx):
        await ctx.send("Você precisa ser administrador para fixar mensagens.")
        return

    channel = find_text_channel(ctx.guild, action.channel) if action.channel else ctx.channel

    if not isinstance(channel, discord.TextChannel):
        await ctx.send("Canal não encontrado para fixar a mensagem.")
        return

    permissions = channel.permissions_for(ctx.guild.me)
    if not permissions.manage_messages or not permissions.read_message_history:
        await ctx.send(
            f"Não tenho permissão para ler histórico ou fixar mensagens em #{channel.name}."
        )
        return

    async for message in channel.history(limit=10, before=ctx.message):
        await message.pin(reason=f"Solicitado por {ctx.author} via !ia")
        await ctx.send(f"Última mensagem válida fixada em #{channel.name}.")
        return

    await ctx.send("Não encontrei nenhuma mensagem recente para fixar.")


async def create_text_channel_action(ctx: commands.Context, action: AIAction) -> None:
    if not is_admin(ctx):
        await ctx.send("Você precisa ser administrador para criar canais.")
        return

    channel_name = clean_channel_name(action.channel_name)
    if not channel_name:
        await ctx.send("Não encontrei um nome válido para criar o canal.")
        return

    existing_channel = find_text_channel(ctx.guild, channel_name)
    if existing_channel is not None:
        await ctx.send(f"O canal #{existing_channel.name} já existe.")
        return

    permissions = ctx.guild.me.guild_permissions
    if not permissions.manage_channels:
        await ctx.send("Não tenho permissão para gerenciar canais.")
        return

    channel = await ctx.guild.create_text_channel(channel_name)
    await ctx.send(f"Canal criado: #{channel.name}")


async def create_trello_task_action(
    ctx: commands.Context,
    action: AIAction,
    trello_settings: TrelloSettings,
) -> None:
    if not can_send_message(ctx):
        await ctx.send(
            "Você precisa ser administrador ou ter o cargo Equipe para criar tarefas pela IA."
        )
        return

    if not action.task_title:
        await ctx.send("Não encontrei o título da tarefa para criar no Trello.")
        return

    if not trello_settings.is_configured:
        await ctx.send(
            "Integração com Trello não configurada. Defina TRELLO_API_KEY, "
            "TRELLO_TOKEN e TRELLO_LIST_ID no arquivo .env."
        )
        return

    description = (
        f"Criado por IA via Discord: {ctx.author} ({ctx.author.id})\n"
        f"Servidor: {ctx.guild.name}\n"
        f"Canal: #{ctx.channel}"
    )
    client = TrelloClient(trello_settings)

    try:
        card = await client.create_card(name=action.task_title, description=description)
    except TrelloError as error:
        await ctx.send(f"Não consegui criar o card no Trello: {error}")
        return

    await ctx.send(f"Tarefa criada no Trello: {card.url}")


def is_admin(ctx: commands.Context) -> bool:
    permissions = getattr(ctx.author, "guild_permissions", None)
    return bool(permissions and permissions.administrator)


def can_send_message(ctx: commands.Context) -> bool:
    if is_admin(ctx):
        return True

    roles = getattr(ctx.author, "roles", [])
    return any(role.name in MESSAGE_ALLOWED_ROLES for role in roles)


def find_text_channel(
    guild: discord.Guild | None,
    channel_name: str,
) -> discord.TextChannel | None:
    if guild is None:
        return None

    cleaned_name = clean_channel_name(channel_name)
    return discord.utils.get(guild.text_channels, name=cleaned_name)


def clean_channel_name(channel_name: str) -> str:
    cleaned = channel_name.strip().lstrip("#").lower()
    cleaned = re.sub(r"\s+", "-", cleaned)
    cleaned = re.sub(r"[^a-z0-9_\-\u00c0-\u017f]", "", cleaned)
    return cleaned.strip("-_")


def is_dangerous_request(request_text: str) -> bool:
    lowered = request_text.lower()
    blocked_phrases = (
        "banir",
        "ban ",
        "expulsar",
        "kick ",
        "apagar canal",
        "deletar canal",
        "excluir canal",
        "apagar mensagens",
        "limpar mensagens",
        "alterar permissão",
        "alterar permissao",
        "alterar cargo",
        "dar cargo",
        "remover cargo",
        "token",
        "secret",
        "variável de ambiente",
        "variavel de ambiente",
    )
    return any(phrase in lowered for phrase in blocked_phrases) or has_blocked_content(
        request_text
    )


def has_blocked_content(text: str) -> bool:
    lowered = text.lower()
    return any(item.lower() in lowered for item in BLOCKED_CONTENT)


def looks_abusive(text: str) -> bool:
    words = {word.strip(".,!?:;").lower() for word in text.split()}
    return bool(words.intersection(ABUSIVE_TERMS))
