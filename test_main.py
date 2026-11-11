"""Pruebas locales sin token, conexión a Discord ni dependencias externas."""
import ast
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch


def cargar_logica():
    # Ejecutar las funciones reales sin iniciar el cliente ni sus decoradores.
    tree = ast.parse(Path(__file__).with_name("main.py").read_text(encoding="utf-8"))
    constantes = {"GTA6_RELEASE_DATE", "CANAL_ID", "CRISIS_EXISTENCIALES", "DESPEDIDA"}
    nodes = []
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module in {"datetime", "math"}:
            nodes.append(node)
        elif isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id in constantes for target in node.targets
        ):
            nodes.append(node)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            node.decorator_list = []
            nodes.append(node)
    namespace = {"ZONA": timezone(timedelta(hours=-3))}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), "main.py", "exec"), namespace)
    return namespace


class BotTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.ns = cargar_logica()
        self.canal = SimpleNamespace(send=AsyncMock())
        self.bot = SimpleNamespace(get_channel=Mock(return_value=self.canal))
        self.ns["bot"] = self.bot

    def fecha(self, day, hour=0, minute=0, second=0):
        return datetime(2026, 11, day, hour, minute, second, tzinfo=self.ns["ZONA"])

    def fijar_hora(self, fecha):
        class Reloj(datetime):
            @classmethod
            def now(cls, tz=None):
                return fecha.astimezone(tz)
        self.ns["datetime"] = Reloj

    async def test_calendario_completo(self):
        for day in (17, 18, 19, 20):
            for hour in range(24):
                with self.subTest(day=day, hour=hour):
                    self.fijar_hora(self.fecha(day, hour))
                    self.canal.send.reset_mock()
                    await self.ns["mensaje_diario"]()
                    debe_enviar = day == 18 or (day in (17, 19) and hour == 0)
                    self.assertEqual(self.canal.send.await_count, int(debe_enviar))
                    if day == 19 and hour == 0:
                        self.canal.send.assert_awaited_once_with(self.ns["DESPEDIDA"])
                    if day == 18:
                        texto = self.canal.send.call_args.args[0]
                        self.assertIn(f"{24 - hour} hora", texto)
                        self.assertIn(self.ns["CRISIS_EXISTENCIALES"][hour // 4], texto)

    async def test_comando_limites_y_redondeo(self):
        casos = [
            (self.fecha(17, 23, 59, 59), "Faltan 2 dias"),
            (self.fecha(18), "Faltan 24 horas"),
            (self.fecha(18, 22, 59, 59), "Faltan 2 horas"),
            (self.fecha(18, 23), "¡Falta 1 hora"),
            (self.fecha(18, 23, 59, 59), "¡Falta 1 hora"),
            (self.fecha(19), self.ns["DESPEDIDA"]),
            (self.fecha(19, 15), self.ns["DESPEDIDA"]),
            (self.fecha(20), "GTA 6 salio hace 1 dias"),
        ]
        for fecha, esperado in casos:
            with self.subTest(fecha=fecha):
                self.fijar_hora(fecha)
                ctx = SimpleNamespace(send=AsyncMock())
                await self.ns["gta6"](ctx)
                ctx.send.assert_awaited_once()
                self.assertIn(esperado, ctx.send.call_args.args[0])

    async def test_canal_ausente(self):
        self.fijar_hora(self.fecha(18, 23))
        self.bot.get_channel.return_value = None
        with patch("builtins.print") as log:
            await self.ns["mensaje_diario"]()
        log.assert_called_once_with("No se encontró el canal")
        self.canal.send.assert_not_awaited()

    async def test_comando_echo(self):
        ctx = SimpleNamespace(send=AsyncMock())
        await self.ns["test"](ctx, "hola mundo")
        ctx.send.assert_awaited_once_with("hola mundo")

    async def test_reconexion_no_duplica_tarea(self):
        tarea = Mock()
        self.ns["mensaje_diario"] = tarea
        for running in (False, True):
            with self.subTest(running=running), patch("builtins.print"):
                tarea.reset_mock()
                tarea.is_running.return_value = running
                await self.ns["on_ready"]()
                self.assertEqual(tarea.start.call_count, int(not running))

    def test_mensajes_caben_en_discord(self):
        mensajes = [self.ns["DESPEDIDA"]] + [
            self.ns["mensaje_ultimas_horas"](h) for h in range(1, 25)
        ]
        for mensaje in mensajes:
            self.assertLessEqual(len(mensaje), 2000)


if __name__ == "__main__":
    unittest.main()
