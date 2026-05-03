import os
import discord
from discord.ext import commands, tasks
from datetime import datetime, date, time
import zoneinfo

GTA6_RELEASE_DATE = date(2026, 11, 19)
ZONA = zoneinfo.ZoneInfo("America/Argentina/Buenos_Aires")

CANAL_ID = 1089246009982451832

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents)

@bot.command()
async def test(ctx, arg):
    await ctx.send(arg)

@bot.command()
async def gta6(ctx):
    today = datetime.now(ZONA).date()
    days_left = (GTA6_RELEASE_DATE - today).days

    if days_left > 0:
        await ctx.send(f"Faltan {days_left} dias para GTA 6.")
    elif days_left == 0:
        await ctx.send("GTA 6 sale hoy.")
    else:
        await ctx.send(f"GTA 6 salio hace {-days_left} dias.")

@tasks.loop(time=time(hour=0, minute=0, tzinfo=ZONA))
async def mensaje_diario():
    canal = bot.get_channel(CANAL_ID)

    if canal is None:
        print("No se encontró el canal")
        return

    today = datetime.now(ZONA).date()
    days_left = (GTA6_RELEASE_DATE - today).days

    if days_left > 0:
        mensaje = f"Faltan {days_left} dias para GTA 6."
    elif days_left == 0:
        mensaje = "GTA 6 sale hoy."
    else:
        mensaje = f"GTA 6 salio hace {-days_left} dias."

    await canal.send(mensaje)

@bot.event
async def on_ready():
    print("Bot is ready!")
    print("------")

    if not mensaje_diario.is_running():
        mensaje_diario.start()

TOKEN = os.getenv("TOKEN")

if TOKEN is None:
    print("ERROR: No se encontró el TOKEN")
else:
    bot.run(TOKEN)