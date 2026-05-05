import discord
from discord.ext import commands

from devbot.commands.general import register_general_commands
from devbot.commands.server_setup import register_server_setup_commands
from devbot.commands.tasks import register_task_commands
from devbot.config import Settings


def create_intents() -> discord.Intents:
    intents = discord.Intents.default()
    intents.message_content = True
    intents.guilds = True
    intents.members = True
    return intents


def create_bot(settings: Settings) -> commands.Bot:
    bot = commands.Bot(command_prefix=settings.command_prefix, intents=create_intents())

    @bot.event
    async def on_ready() -> None:
        print(f"DEVbot conectado como {bot.user}")

    register_general_commands(bot)
    register_server_setup_commands(bot)
    register_task_commands(bot, settings.trello)

    return bot
