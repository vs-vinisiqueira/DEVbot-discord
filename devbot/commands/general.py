from discord.ext import commands


def register_general_commands(bot: commands.Bot) -> None:
    @bot.command(name="ping")
    async def ping(ctx: commands.Context) -> None:
        await ctx.send("Pong! O DEVbot está online.")
