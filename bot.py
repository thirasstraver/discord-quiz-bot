import discord
from discord.ext import commands
import asyncio
import os

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = 1478505267737006173

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot is online als {bot.user}")

bot.run(TOKEN)