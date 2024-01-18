from telegram import Bot
from telegram import InputFile

# Coloca aquí tu token de bot obtenido del BotFather
TOKEN = '6373598795:AAEE6lTAMEH_ldL0Mm9BgN1YYwVzXLeyiF0'

# ID del chat al que deseas enviar el mensaje
# Puedes obtenerlo ejecutando el script una vez y revisando la salida
CHAT_ID = '1748694292'

# Ruta al archivo que deseas adjuntar
archivo_adjunto = '/home/pi/Proyecto/3d.obj'

def enviar_archivo_adjunto():
    try:
        # Crea una instancia del bot
        bot = Bot(token=TOKEN)

        # Envia el archivo adjunto al chat especificado
        with open(archivo_adjunto, 'rb') as archivo:
            bot.send_document(chat_id=CHAT_ID, document=InputFile(archivo))

        print("Archivo adjunto enviado con éxito.")
    except Exception as e:
        print(f"Ocurrió un error: {e}")

if __name__ == "__main__":
    enviar_archivo_adjunto()

import asyncio
from telegram import Bot
from telegram import InputFile

# Coloca aquí tu token de bot obtenido del BotFather
TOKEN = '6373598795:AAEE6lTAMEH_ldL0Mm9BgN1YYwVzXLeyiF0'

# ID del chat al que deseas enviar el mensaje
# Puedes obtenerlo ejecutando el script una vez y revisando la salida
CHAT_ID = '1748694292'

# Ruta al archivo que deseas adjuntar
archivo_adjunto = '/home/pi/AA-Scan/point_cloud.obj'

async def enviar_archivo_adjunto():
    try:
        # Crea una instancia del bot
        bot = Bot(token=TOKEN)

        # Envia el archivo adjunto al chat especificado
        with open(archivo_adjunto, 'rb') as archivo:
            await bot.send_document(chat_id=CHAT_ID, document=InputFile(archivo))

        print("Archivo adjunto enviado con éxito.")
    except Exception as e:
        print(f"Ocurrió un error: {e}")

if __name__ == "__main__":
    # Inicia el bucle de eventos asíncronos
    loop = asyncio.get_event_loop()
    loop.run_until_complete(enviar_archivo_adjunto())