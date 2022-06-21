import aiohttp
import asyncio



# async def admin_request(
#         method, path, data=None, text=False, params=None, headers=None
#     ) -> ClientResponse:

        #params = {k: v for (k, v) in (params or {}).items() if v is not None}

        # async with self.client_session.request(
        #     method, path, json=data, params=params, headers=headers
        # ) as resp:
        #     resp_text = await resp.text()
        #     try:
        #         resp.raise_for_status()
        #     except Exception as e:
        #         # try to retrieve and print text on error
        #         raise Exception(f"Error: {resp_text}") from e
        #     if not resp_text and not text:
        #         return None
        #     if not text:
        #         try:
        #             return json.loads(resp_text)
        #         except json.JSONDecodeError as e:
        #             raise Exception(f"Error decoding JSON: {resp_text}") from e
        #     return resp_text 

async def admin_request(
        session, method, path, data=None, text=False, params=None, headers=Noce
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

    # async with session.post('/connections/create-invitation') as response:

    #     invitacion = await response.json() 

    #     return invitacion




async def main():

    # a ClientSession() le podemos añadir una URL_base que podemos usar
    # en todas las peticiones posteriores: clientSession(Base_URL)
    async with aiohttp.ClientSession(admin_api) as session:

        invit = await crear_invitacion(session)

        print(invit)

        # invitacion = await crear_invitacion(session)

        # print(invitacion)







admin_api = 'http://0.0.0.0:11000'


asyncio.run(main())
# loop = asyncio.get_event_loop()
# loop.run_until_complete(main())
