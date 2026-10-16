import os
from math import ceil
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

@tasks.loop(time=[time(hour=hora, minute=0, tzinfo=ZONA) for hora in range(24)])
async def mensaje_diario():
    ahora = datetime.now(ZONA)
    lanzamiento = datetime.combine(GTA6_RELEASE_DATE, time.min, tzinfo=ZONA)
    segundos_restantes = (lanzamiento - ahora).total_seconds()
    ultimas_24_horas = 0 < segundos_restantes <= 24 * 60 * 60

    if not ultimas_24_horas and ahora.hour != 0:
        return

    canal = bot.get_channel(CANAL_ID)

    if canal is None:
        print("No se encontró el canal")
        return

    today = ahora.date()
    days_left = (GTA6_RELEASE_DATE - today).days

    if ultimas_24_horas:
        horas_restantes = ceil(segundos_restantes / 3600)
        if horas_restantes == 1:
            mensaje = "¡Falta 1 hora para GTA 6!"
        else:
            mensaje = f"Faltan {horas_restantes} horas para GTA 6."
    elif days_left > 0:
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

