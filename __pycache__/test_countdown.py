"""Pruebas aisladas del bot: no cargan TOKEN ni se conectan a Discord.
Ejecutar con Python 3.10 o superior desde esta carpeta.
"""
import ast
import asyncio
from contextlib import redirect_stdout
from datetime import datetime, date, time, timedelta, timezone
from io import StringIO
from math import ceil
from pathlib import Path
from types import SimpleNamespace
import unittest

SOURCE = Path(__file__).resolve().parent.parent / 'main.py'
TREE = ast.parse(SOURCE.read_text(encoding='utf-8-sig'))
ZONE = timezone(timedelta(hours=-3))

class Clock(datetime):
    current = datetime(2026, 11, 17, tzinfo=ZONE)
    @classmethod
    def now(cls, tz=None):
        return cls.current.astimezone(tz)

class Loop:
    def __init__(self, fn, schedule):
        self.fn, self.schedule = fn, schedule
        self.running, self.starts = False, 0
    async def __call__(self):
        await self.fn()
    def is_running(self):
        return self.running
    def start(self):
        self.running = True
        self.starts += 1

class Bot:
    def __init__(self):
        self.messages = []
        self.channel = self
        self.lookups = []
        self.send_error = None
    def command(self):
        return lambda fn: fn
    def event(self, fn):
        return fn
    def get_channel(self, channel_id):
        self.lookups.append(channel_id)
        return self.channel
    async def send(self, message):
        if self.send_error:
            raise self.send_error
        self.messages.append(message)

def load_bot():
    bot = Bot()
    tasks = SimpleNamespace(loop=lambda **kw: lambda fn: Loop(fn, kw['time']))
    env = dict(bot=bot, tasks=tasks, datetime=Clock, date=date, time=time, ceil=ceil,
               ZONA=ZONE, GTA6_RELEASE_DATE=date(2026, 11, 19), CANAL_ID=1089246009982451832)
    functions = [n for n in TREE.body if isinstance(n, ast.AsyncFunctionDef)]
    exec(compile(ast.Module(body=functions, type_ignores=[]), str(SOURCE), 'exec'), env)
    return bot, env

class CountdownTests(unittest.TestCase):
    def setUp(self):
        self.bot, self.env = load_bot()
    def at(self, value):
        Clock.current = datetime.fromisoformat(value).replace(tzinfo=ZONE)
        self.bot.messages.clear()
        asyncio.run(self.env['mensaje_diario']())
        return self.bot.messages.copy()
    def test_source_compiles(self):
        compile(TREE, str(SOURCE), 'exec')
    def test_schedule_has_each_local_hour_once(self):
        schedule = self.env['mensaje_diario'].schedule
        self.assertEqual(len(schedule), 24)
        self.assertEqual(len(set(schedule)), 24)
        for hour, slot in enumerate(schedule):
            with self.subTest(hour=hour):
                self.assertEqual((slot.hour, slot.minute, slot.second), (hour, 0, 0))
                self.assertEqual(slot.utcoffset(), timedelta(hours=-3))
    def test_all_24_hourly_messages_and_execution_delays(self):
        for hour in range(24):
            for suffix in ('00:00', '00:00.500000', '00:30', '59:59.999999'):
                with self.subTest(hour=hour, suffix=suffix):
                    hours = 24 - hour
                    expected = ('¡Falta 1 hora para GTA 6!' if hours == 1
                                else f'Faltan {hours} horas para GTA 6.')
                    self.assertEqual(self.at(f'2026-11-18T{hour:02d}:{suffix}'), [expected])
    def test_countdown_boundaries(self):
        cases = [
            ('2026-11-17T23:59:59.999999', []),
            ('2026-11-18T00:00:00', ['Faltan 24 horas para GTA 6.']),
            ('2026-11-18T22:59:59.999999', ['Faltan 2 horas para GTA 6.']),
            ('2026-11-18T23:00:00', ['¡Falta 1 hora para GTA 6!']),
            ('2026-11-18T23:59:59.999999', ['¡Falta 1 hora para GTA 6!']),
            ('2026-11-19T00:00:00', ['GTA 6 sale hoy.']),
            ('2026-11-19T01:00:00', []),
        ]
        for value, expected in cases:
            with self.subTest(value=value): self.assertEqual(self.at(value), expected)
    def test_daily_messages_before_and_after_release(self):
        cases = [('2026-10-16', 'Faltan 34 dias para GTA 6.'),
                 ('2026-11-17', 'Faltan 2 dias para GTA 6.'),
                 ('2026-11-20', 'GTA 6 salio hace 1 dias.'),
                 ('2027-01-01', 'GTA 6 salio hace 43 dias.')]
        for day, expected in cases:
            with self.subTest(day=day): self.assertEqual(self.at(day+'T00:00:00'), [expected])
    def test_no_extra_messages_outside_last_day(self):
        for day in ('2026-10-16', '2026-11-17', '2026-11-19', '2026-11-20'):
            for hour in range(1, 24):
                with self.subTest(day=day, hour=hour):
                    self.assertEqual(self.at(f'{day}T{hour:02d}:00:00'), [])
        self.assertEqual(self.bot.lookups, [])
    def test_three_day_simulation_has_no_daily_hourly_overlap(self):
        sent = []
        for day in (17, 18, 19):
            for hour in range(24):
                messages = self.at(f'2026-11-{day}T{hour:02d}:00:00')
                self.assertLessEqual(len(messages), 1)
                sent.extend(messages)
        self.assertEqual(len(sent), 26)
        self.assertEqual(sent[1], 'Faltan 24 horas para GTA 6.')
        self.assertEqual(sent[-2:], ['¡Falta 1 hora para GTA 6!', 'GTA 6 sale hoy.'])
    def test_missing_channel_skips_and_logs(self):
        self.bot.channel = None
        with redirect_stdout(StringIO()) as output:
            self.assertEqual(self.at('2026-11-18T12:00:00'), [])
        self.assertIn('No se encontró el canal', output.getvalue())
    def test_repeated_ready_does_not_start_duplicate_task(self):
        with redirect_stdout(StringIO()):
            for _ in range(5): asyncio.run(self.env['on_ready']())
        self.assertEqual(self.env['mensaje_diario'].starts, 1)
    def test_gta6_command_still_responds_in_days(self):
        for value, expected in [('2026-11-17', 'Faltan 2 dias para GTA 6.'),
                                ('2026-11-18', 'Faltan 1 dias para GTA 6.'),
                                ('2026-11-19', 'GTA 6 sale hoy.'),
                                ('2026-11-20', 'GTA 6 salio hace 1 dias.')]:
            with self.subTest(day=value):
                Clock.current = datetime.fromisoformat(value).replace(tzinfo=ZONE)
                self.bot.messages.clear()
                asyncio.run(self.env['gta6'](self.bot))
                self.assertEqual(self.bot.messages, [expected])
    def test_test_command_echoes_argument(self):
        asyncio.run(self.env['test'](self.bot, 'hola'))
        self.assertEqual(self.bot.messages, ['hola'])
    def test_documents_send_failure_is_currently_propagated(self):
        self.bot.send_error = PermissionError('Permiso de envio denegado')
        with self.assertRaises(PermissionError): self.at('2026-11-18T12:00:00')
        self.assertEqual(self.bot.messages, [])
    def test_utc_instant_is_converted_to_argentina_time(self):
        Clock.current = datetime(2026, 11, 18, 3, tzinfo=timezone.utc)
        asyncio.run(self.env['mensaje_diario']())
        self.assertEqual(self.bot.messages, ['Faltan 24 horas para GTA 6.'])
        self.bot.messages.clear()
        Clock.current = datetime(2026, 11, 19, 3, tzinfo=timezone.utc)
        asyncio.run(self.env['mensaje_diario']())
        self.assertEqual(self.bot.messages, ['GTA 6 sale hoy.'])

if __name__ == '__main__':
    unittest.main(verbosity=2)
