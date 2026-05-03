import os
import discord
from discord.ext import commands
from datetime import datetime, date
import zoneinfo

# Fecha de salida GTA 6
GTA6_RELEASE_DATE = date(2026, 11, 19)

# Zona horaria Argentina
ZONA = zoneinfo.ZoneInfo("America/Argentina/Buenos_Aires")

# Intents necesarios
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents)

# Comando de prueba
@bot.command()
async def test(ctx, arg):
    await ctx.send(arg)

# Comando GTA 6
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

# Evento cuando el bot está listo
@bot.event
async def on_ready():
    print("Bot is ready!")
    print("------")

# Obtener token desde Railway
TOKEN = os.getenv("TOKEN")

if TOKEN is None:
    print("ERROR: No se encontró el TOKEN")
else:
    bot.run(TOKEN)