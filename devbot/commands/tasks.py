from discord.ext import commands

from devbot.config import TrelloSettings
from devbot.trello import TrelloClient, TrelloError


def register_task_commands(bot: commands.Bot, trello_settings: TrelloSettings) -> None:
    @bot.command(name="tarefa")
    async def create_task(ctx: commands.Context, *, title: str) -> None:
        if not trello_settings.is_configured:
            await ctx.send(
                "Integração com Trello não configurada. Defina TRELLO_API_KEY, "
                "TRELLO_TOKEN e TRELLO_LIST_ID no arquivo .env."
            )
            return

        description = (
            f"Criado por: {ctx.author} ({ctx.author.id})\n"
            f"Servidor: {ctx.guild.name if ctx.guild else 'Mensagem direta'}\n"
            f"Canal: #{ctx.channel}"
        )

        client = TrelloClient(trello_settings)

        try:
            card = await client.create_card(name=title, description=description)
        except TrelloError as error:
            await ctx.send(f"Não consegui criar o card no Trello: {error}")
            return

        await ctx.send(f"Tarefa criada no Trello: {card.url}")

    @create_task.error
    async def create_task_error(
        ctx: commands.Context,
        error: commands.CommandError,
    ) -> None:
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Use: !tarefa descrição da tarefa")
        else:
            await ctx.send(f"Ocorreu um erro: {error}")
