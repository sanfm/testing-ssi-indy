import aiohttp
import asyncio
import os

from modulos import peticiones
from modulos import utils
from modulos.hookclass import WebHook



async def main():



    hook = WebHook(webhook_port)

    # iniciar servidor a la escucha de eventos
    await hook.webhook_server_init()


    # a ClientSession() le podemos añadir una URL_base que podemos usar
    # en todas las peticiones posteriores: clientSession(Base_URL)
    async with aiohttp.ClientSession(admin_api) as session:

        invit = await peticiones.crear_invitacion(session)
        print(invit)


        options = "1) Generar nueva invitación"
        async for option in utils.prompt_loop(options):

            if option is not None:
                option = option.strip()

            if option is None or option in "xX":
                break

            if option == "1":
                invit = await peticiones.crear_invitacion(session)
                print(invit)


    await hook.webhook_server_terminate()
    os._exit(1)
            





webhook_port = 11001
admin_api = 'http://0.0.0.0:11000'

asyncio.run(main())
