import aiohttp
import asyncio


async def main():

    # a ClientSession() le podemos añadir una URL_base que podemos usar
    # en todas las peticiones posteriores: clientSession(Base_URL)
    async with aiohttp.ClientSession('http://0.0.0.0:11000') as session:
        async with session.post('/connections/create-invitation') as response:

            print("Status:", response.status)
            #print("Content-type:", response.headers['content-type'])

            resp = await response.json()
            #print("Body:", html[:15], "...")
            print(resp)




#admin_api = 'http://0.0.0.0:11000'

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
