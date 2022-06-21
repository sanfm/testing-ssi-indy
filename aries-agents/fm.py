import aiohttp
import asyncio
import os

from modulos import peticiones
from modulos import utils


async def main():

    # a ClientSession() le podemos añadir una URL_base que podemos usar
    # en todas las peticiones posteriores: clientSession(Base_URL)
    async with aiohttp.ClientSession(admin_api) as session:

        options = "    (1) Input New Invitation\n" "    (2) Send Message\n"
        async for option in utils.prompt_loop(options):

            if option is not None:
                option = option.strip()

            if option is None or option in "xX":
                break

            elif option == "1":
                utils.log_status("Introducir detalles de la invitacion")
                conexion = peticiones.recibir_invitacion(session)



    os._exit(1)


        #invit = await peticiones.crear_invitacion(session)

        #print(invit)








admin_api = 'http://0.0.0.0:11001'

asyncio.run(main())
