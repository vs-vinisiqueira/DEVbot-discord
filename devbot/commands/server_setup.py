import discord
from discord.ext import commands

from devbot.constants import CHANNEL_STRUCTURE, ROLES


def register_server_setup_commands(bot: commands.Bot) -> None:
    @bot.command(name="setup")
    @commands.has_permissions(administrator=True)
    async def setup(ctx: commands.Context) -> None:
        guild = ctx.guild

        if guild is None:
            await ctx.send("Esse comando só pode ser usado dentro de um servidor.")
            return

        await ctx.send("Iniciando configuração do servidor acadêmico...")

        for role_name in ROLES:
            existing_role = discord.utils.get(guild.roles, name=role_name)

            if existing_role is None:
                await guild.create_role(name=role_name)
                await ctx.send(f"Cargo criado: {role_name}")
            else:
                await ctx.send(f"Cargo já existe: {role_name}")

        for category_name, channels in CHANNEL_STRUCTURE.items():
            category = discord.utils.get(guild.categories, name=category_name)

            if category is None:
                category = await guild.create_category(category_name)
                await ctx.send(f"Categoria criada: {category_name}")
            else:
                await ctx.send(f"Categoria já existe: {category_name}")

            for channel_name in channels:
                existing_channel = discord.utils.get(
                    guild.text_channels,
                    name=channel_name,
                )

                if existing_channel is None:
                    await guild.create_text_channel(channel_name, category=category)
                    await ctx.send(f"Canal criado: #{channel_name}")
                else:
                    await ctx.send(f"Canal já existe: #{channel_name}")

        await ctx.send("Servidor configurado com sucesso.")

    @setup.error
    async def setup_error(ctx: commands.Context, error: commands.CommandError) -> None:
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Você precisa ser administrador para usar esse comando.")
        else:
            await ctx.send(f"Ocorreu um erro: {error}")
