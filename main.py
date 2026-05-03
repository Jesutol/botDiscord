import os
import discord
from discord.ext import commands
from datetime import date


GTA6_RELEASE_DATE = date(2026, 11, 19)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents)

@bot.command()
async def test(ctx, arg):
    await ctx.send(arg)

@bot.command()
async def gta6(ctx):
    today = date.today()
    days_left = (GTA6_RELEASE_DATE - today).days

    if days_left > 0:
        await ctx.send(f"Faltan {days_left} dias para GTA 6.")
    elif days_left == 0:
        await ctx.send("GTA 6 sale hoy.")
    else:
        await ctx.send(f"GTA 6 salio hace {-days_left} dias.")

@bot.event
async def on_ready():
    print( "Bot is ready!" )
    print('------')

bot.run(os.getenv("TOKEN"))   