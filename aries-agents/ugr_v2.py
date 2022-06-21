import aiohttp
import asyncio



async def crear_invitacion(
        session,
        use_did_exchange: bool = False
        ):
    async with session.post('/connections/create-invitation') as response:

        invitacion = await response.json() 

        return invitacion




async def main():

    # a ClientSession() le podemos añadir una URL_base que podemos usar
    # en todas las peticiones posteriores: clientSession(Base_URL)
    async with aiohttp.ClientSession('http://0.0.0.0:11000') as session:

        invitacion = await crear_invitacion(session)

        print(invitacion)



#admin_api = 'http://0.0.0.0:11000'


asyncio.run(main())
# loop = asyncio.get_event_loop()
# loop.run_until_complete(main())
