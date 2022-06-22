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
                conexion = await peticiones.recibir_invitacion(session)
                print(conexion)
                print('conexion es :{}'.format(type(conexion)))

                con_id = conexion.get("connection_id")

                # Responder a la inviatión
                algo = peticiones.acetpar_invitacion(session, con_id)
                print(algo)

    os._exit(1)











admin_api = 'http://0.0.0.0:11001'

asyncio.run(main())
