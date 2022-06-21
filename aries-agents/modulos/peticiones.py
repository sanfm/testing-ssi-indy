import aiohttp
import asyncio




async def admin_request(
        session, method, path, data=None, text=False, params=None, headers=None
        ) -> aiohttp.ClientResponse:

    async with session.request(method, path, json=data, params=params, headers=headers) as response:

        resp = await response.json() 

    return resp


async def crear_invitacion(
        session,
        use_did_exchange: bool = False
        ):

    invitacion = await admin_request(session, 'POST', '/connections/create-invitation')

    return invitacion





# async def main():

#     # a ClientSession() le podemos añadir una URL_base que podemos usar
#     # en todas las peticiones posteriores: clientSession(Base_URL)
#     async with aiohttp.ClientSession(admin_api) as session:

#         invit = await crear_invitacion(session)

#         print(invit)



# admin_api = 'http://0.0.0.0:11000'


#asyncio.run(main())
