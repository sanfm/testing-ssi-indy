import aiohttp
import asyncio


async def main():

    async with aiohttp.ClientSession() as session:
        async with session.get(admin_api + "/connections/create-invitation") as response:

            print("Status:", response.status)
            print("Content-type:", response.headers['content-type'])

            resp = await response.text()
            #print("Body:", html[:15], "...")
            print(resp)




admin_api = 'http://0.0.0.0:11000'

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
