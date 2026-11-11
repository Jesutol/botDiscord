# Bot de Discord: cuenta regresiva para GTA 6

## Descripción

Este proyecto contiene un bot de Discord escrito en Python. Informa cuánto falta para la fecha de lanzamiento de GTA 6 configurada en el código y publica avisos automáticos en un canal.

## Archivos principales

- `main.py`: comandos, programación de mensajes y conexión a Discord.
- `requirements.txt`: dependencia `discord.py==2.3.2`.
- `Procfile`: inicia el proceso con `worker: python main.py`.
- `runtime.txt`: declara Python 3.10.

## Configuración actual

- Fecha objetivo: `19 de noviembre de 2026`, definida en `GTA6_RELEASE_DATE`. Es un valor fijo; el bot no consulta ni verifica la fecha oficial del lanzamiento.
- Zona horaria: `America/Argentina/Buenos_Aires`.
- Canal para avisos: `1089246009982451832`, definido en `CANAL_ID`.
- Prefijo de comandos: `$`.
- Credencial: variable de entorno `TOKEN`. Si no está definida, el programa muestra un error y no conecta. No guardar credenciales en el código ni en archivos versionados.

## Comandos

- `$gta6`: responde cuántos días faltan; durante las últimas 24 horas muestra las horas restantes y la crisis correspondiente. El día del lanzamiento devuelve la despedida; después informa los días transcurridos con un agradecimiento.
- `$test argumento`: devuelve el argumento recibido. Para incluir varias palabras en un único argumento, se deben usar comillas.

## Mensajes automáticos

- La tarea `mensaje_diario` se inicia desde `on_ready`, siempre que no esté ejecutándose.
- Se programa para cada hora en punto, según la zona horaria configurada.
- Fuera de las últimas 24 horas, solo publica a medianoche.
- Durante las últimas 24 horas, publica cada hora las horas restantes, redondeadas hacia arriba, junto con una frase de miedo a terminar su tarea. `mensaje_ultimas_horas` avanza por las seis frases de `CRISIS_EXISTENCIALES` en etapas de cuatro horas.
- La cuenta regresiva termina a las 00:00 de la fecha configurada; no representa una hora oficial de lanzamiento verificada.
- A medianoche del lanzamiento publica `DESPEDIDA`, un cierre emotivo con un guiño a The Truman Show. Después deja de enviar avisos automáticos; los comandos siguen disponibles. La tarea permanece programada, pero omite los envíos posteriores.
- La crisis personifica al bot como un personaje vulnerable: siente el paso del tiempo, teme ser olvidado o apagado y pide un propósito para mañana. Mantener una voz íntima y asustada, como ficción dentro de la broma. Es solo texto; no cambia el funcionamiento del programa.
- Si el bot está apagado cuando corresponde un aviso, no recupera los mensajes pendientes al reiniciarse.
- El canal se obtiene mediante `bot.get_channel`. Si no se encuentra, se registra un mensaje y se omite el envío.

## Ejecución y requisitos

1. Instalar las dependencias de `requirements.txt`.
2. Configurar la variable de entorno `TOKEN` con el token del bot.
3. Habilitar el intent de contenido de mensajes en el portal de desarrolladores de Discord; el código ya solicita `message_content`.
4. Asegurar que el bot tenga acceso al canal configurado y permiso para enviar mensajes.
5. Ejecutar `python main.py`.

## Indicaciones para cambios

- Mantener coherente el cálculo de fechas entre el comando y la tarea automática.
- Preservar el uso explícito de la zona horaria de Buenos Aires.
- No iniciar el bot ni enviar mensajes reales a Discord como parte de una revisión del código, salvo que el usuario lo solicite.
- Actualizar este archivo cuando cambien los comandos, la configuración o el comportamiento de los avisos.

## Alcance de la revisión inicial

La descripción anterior proviene de una lectura del código. No se ejecutó el bot ni se verificaron su conexión, permisos o configuración externa en Discord.

## Pruebas locales

- Ejecutar `python -m unittest -v test_main`.
- `test_main.py` ejecuta las funciones del código mediante AST, sin iniciar el bot ni cargar Discord. Simula reloj, canal y contexto; usa UTC-3 para las fechas de Buenos Aires de noviembre de 2026.
- Cubre 96 horarios del 17 al 20 de noviembre, las seis etapas, redondeo en los límites, despedida, silencio posterior, comandos, canal ausente, reconexión y longitud de mensajes.
- No verifica integración con discord.py, carga de ZoneInfo, permisos, credenciales ni el programador real. Las seis pruebas pasaron con Python 3.15.2; no se verificó el runtime declarado de Python 3.10.
