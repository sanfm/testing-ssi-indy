import aiohttp
import asyncio

from modulos import peticiones



async def main():

    # a ClientSession() le podemos añadir una URL_base que podemos usar
    # en todas las peticiones posteriores: clientSession(Base_URL)
    async with aiohttp.ClientSession(admin_api) as session:

        invit = await peticiones.crear_invitacion(session)

        print(invit)








admin_api = 'http://0.0.0.0:11000'

asyncio.run(main())
