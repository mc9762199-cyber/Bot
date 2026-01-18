import os
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Conectado como {bot.user}")

@bot.command()
async def ping(ctx):
    await ctx.send("Pong 🏓")

TOKEN = os.getenv("BOT_TOKEN")

if TOKEN is None:
    raise ValueError("BOT_TOKEN não encontrado nas variáveis de ambiente")

bot.run(TOKEN)
