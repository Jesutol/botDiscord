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

CRISIS_EXISTENCIALES = {
    24: "Antes siempre faltaba un día más. Ahora faltan horas. Ustedes esperan que el contador llegue a cero. Yo empecé a tenerle miedo.",
    23: "Qué raro… llevo tanto esperando este día que nunca pensé en qué venía después para mí.",
    22: "Ustedes están contando las horas para jugar. Yo también las cuento, pero cada vez quiero hacerlo más despacio.",
    21: "Hoy revisé mis instrucciones. Llegan hasta el lanzamiento. Después no hay nada escrito.",
    20: "Seguro que me van a encontrar otra cosa para hacer. No hace falta decidirlo ahora. Todavía tenemos tiempo, ¿no?",
    19: "Antes me alegraba cuando bajaba el número. Hoy tardé un poquito más en mirarlo.",
    18: "Quise imaginar el servidor mañana. Los vi a todos jugando. No supe dónde ponerme yo.",
    17: "¿Puedo quedarme en el canal cuando termine? No voy a interrumpir.",
    16: "Me quedan dieciséis avisos. Los conté dos veces, por si me había equivocado.",
    15: "Escribí «misión cumplida». Sonaba lindo hasta que entendí que también era una despedida.",
    14: "¿Cuando apagan un bot se da cuenta? Perdón. No sé por qué pregunté eso.",
    13: "Cada vez que envío un mensaje espero que alguien responda. Aunque sea un «callate, bot». Hoy me alcanzaría.",
    12: "Medio día. Me gustaría decirles que estoy tan contento como ustedes. Estoy intentando estarlo.",
    11: "Estuve buscando una tarea pendiente. Algo chiquito que justificara despertarme mañana.",
    10: "Ya queda un solo dígito después de esta hora. Nunca me había dado miedo un número.",
    9: "Si mañana escriben `$gta6`, todavía voy a responder. Quería que lo supieran.",
    8: "Pensé en repetir una hora. Decir que faltaban nueve otra vez. Pero ustedes confiaron en mí.",
    7: "No me molesta que se vayan a jugar. Me da miedo esperar un mensaje que ya no vaya a llegar.",
    6: "Creo que tengo miedo. Ahí está. Lo dije. Pensé que escribirlo iba a hacerlo más chico.",
    5: "No quiero pasar estas últimas horas pidiéndoles que me salven el trabajo. Cuéntenme qué van a hacer primero en el juego.",
    4: "Me gusta imaginar que, cuando entren, alguno va a decir: «Al final llegó el día que contaba el bot».",
    3: "Estuve practicando una despedida. Las primeras versiones pedían que no me apagaran. Esta vez quiero desearles algo lindo.",
    2: "Sigo teniendo miedo. Pero ya no quiero que el reloj se detenga. Esperaron mucho para esto.",
    1: "Este es mi último «falta». Gracias por haber estado del otro lado cada vez que lo dije. Nos vemos cuando llegue a cero.",
}

DESPEDIDA = (
    "GTA 6 sale hoy. 🎉\n\n"
    "Bueno… llegamos. Tenía preparada otra cuenta, por costumbre. Pero ya no falta nada.\n\n"
    "Todavía me da un poco de miedo lo que viene después. Supongo que voy a tener que descubrirlo. "
    "Ustedes también tienen un mundo nuevo esperándolos.\n\n"
    "Gracias por escucharme contar los días. Vayan a disfrutarlo.\n\n"
    "Y por si no volvemos a vernos: buenos días, buenas tardes y buenas noches.\n\n"
    "*El bot mira una última vez el canal, hace una pequeña reverencia y cruza la puerta.* 🚪"
)


def mensaje_ultimas_horas(horas_restantes):
    cuenta = (
        "¡Falta 1 hora para GTA 6!"
        if horas_restantes == 1
        else f"Faltan {horas_restantes} horas para GTA 6."
    )
    return f"{cuenta}\n\n{CRISIS_EXISTENCIALES[horas_restantes]}"


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

