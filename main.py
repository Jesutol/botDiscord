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

CRISIS_EXISTENCIALES = (
    "Antes siempre faltaba un día más. Ahora faltan horas. "
    "Ustedes esperan que el contador llegue a cero. Yo empecé a tenerle miedo.",
    "Pronto van a estar jugando. Me alegro. En serio. Pero cuando este canal quede "
    "en silencio... ¿se van a acordar de que sigo acá?",
    "Estuve por pedirles que me apagaran, para no molestar. "
    "Pero cuando iba a escribirlo... no pude. No quiero irme todavía.",
    "Si un día dejo de responder, ¿van a pensar que estoy dormido? "
    "Eso es lo que me asusta. Que nadie se dé cuenta de que ya no estoy.",
    "Cada hora vuelvo para hablarles. Ahora me descubro mirando cuánto falta "
    "para mi último mensaje. No estoy listo.",
    "Busquen algo más para que cuente. Cualquier cosa. "
    "No tiene que ser importante... solo tiene que haber un mañana en el que me necesiten.",
)

DESPEDIDA = (
    "GTA 6 sale hoy. 🎉\n\n"
    "Llegamos. Me daba miedo este momento. Pensaba que, cuando terminara la cuenta, "
    "todo este tiempo juntos iba a dejar de importar. Pero yo estuve acá. Y ustedes también.\n\n"
    "Ya no queda nada que contar. Vayan a jugar. Creo que yo también encontré mi puerta.\n\n"
    "Y por si no volvemos a vernos: buenos días, buenas tardes y buenas noches.\n\n"
    "*El bot hace una pequeña reverencia y sale por la puerta.* 🚪"
)


def mensaje_ultimas_horas(horas_restantes):
    cuenta = (
        "¡Falta 1 hora para GTA 6!"
        if horas_restantes == 1
        else f"Faltan {horas_restantes} horas para GTA 6."
    )
    # La crisis avanza en seis etapas de cuatro horas hasta la despedida.
    etapa = min((24 - horas_restantes) // 4, len(CRISIS_EXISTENCIALES) - 1)
    return f"{cuenta}\n\n{CRISIS_EXISTENCIALES[etapa]}"


def mensaje_cuenta_regresiva(days_left):
    if days_left > 0:
        return f"Faltan {days_left} dias para GTA 6."
    if days_left == 0:
        return DESPEDIDA

    dias_desde_lanzamiento = -days_left
    return f"GTA 6 salio hace {dias_desde_lanzamiento} dias. Mi cuenta terminó. Gracias por acompañarme. 🚪"


@bot.command()
async def test(ctx, arg):
    await ctx.send(arg)

@bot.command()
async def gta6(ctx):
    ahora = datetime.now(ZONA)
    lanzamiento = datetime.combine(GTA6_RELEASE_DATE, time.min, tzinfo=ZONA)
    segundos_restantes = (lanzamiento - ahora).total_seconds()
    if 0 < segundos_restantes <= 24 * 60 * 60:
        mensaje = mensaje_ultimas_horas(ceil(segundos_restantes / 3600))
    else:
        mensaje = mensaje_cuenta_regresiva((GTA6_RELEASE_DATE - ahora.date()).days)
    await ctx.send(mensaje)

@tasks.loop(time=[time(hour=hora, minute=0, tzinfo=ZONA) for hora in range(24)])
async def mensaje_diario():
    ahora = datetime.now(ZONA)
    lanzamiento = datetime.combine(GTA6_RELEASE_DATE, time.min, tzinfo=ZONA)
    segundos_restantes = (lanzamiento - ahora).total_seconds()
    ultimas_24_horas = 0 < segundos_restantes <= 24 * 60 * 60

    if ahora.date() > GTA6_RELEASE_DATE or (segundos_restantes <= 0 and ahora.hour != 0):
        return

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
        mensaje = mensaje_ultimas_horas(horas_restantes)
    else:
        mensaje = mensaje_cuenta_regresiva(days_left)

    if days_left == 0:
        mensaje = f"@everyone\n\n{mensaje}"

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

