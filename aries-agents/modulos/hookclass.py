from aiohttp import web
import asyncio
import json





class WebHook:
    
    def __init__(self, webhook_port):
        self.webhook_port = webhook_port
        self.webhook_site = None
        self.webhook_url = None



    async def webhook_server_terminate(self):
        if self.webhook_site:
            await self.webhook_site.stop()
            print("parando webhook server")



    async def webhook_server_init(self):
        self.webhook_url = f"http://localhost:{str(self.webhook_port)}/webhooks"
        app = web.Application()
        app.add_routes(
                [
                    web.post("/webhooks/topic/connections/", self.conn_handler),
                    # web.post("/webhooks/topic/{topic}/", self.receive_webhook),
                    web.get('/', self.hello)
                ]
        )
        runner = web.AppRunner(app)
        await runner.setup()
        self.webhook_site = web.TCPSite(runner, '0.0.0.0', self.webhook_port)
        await self.webhook_site.start()
        print("escuchando: http://localhost:{}".format(self.webhook_port))


    async def conn_handler(self, request):
        # data = await request.json()
        # print(data)
        # return web.Response(status=200)
        data = await request.json()
        # print(type(data))
        print(data.get("state"))
        return web.Response(status=200)



    async def hello(self, request):
        return web.Response(text="Hello, world")



    # async def receive_webhook(self, request):
    #     topic = request.match_info["topic"].replace("-", "_")
    #     req_data = await request.json()
    #     await self.webhook_handler(topic, req_data, request.headers)
    #     # print(req_data)
    #     return web.Response(status=200)




    # async def webhook_handler(self, topic, payload, headers):
    #     if topic != "webhook":
    #         handler = f"handle_{topic}"
    #         method = getattr(self, handler, None)
    #         if method:
    #             EVENT_LOGGER.debug(
    #                 "Agent called controller webhook: %s%s%s",
    #                 handler,
    #                 f"\nPOST {self.webhook_url}/topic/{topic}/",
    #                 (f" with payload: \n{repr_json(payload)}\n" if payload else ""),
    #             )
    #             asyncio.get_event_loop().create_task(method(payload))
    #         else:
    #             log_msg(
    #                 f"Error: agent {self.ident} "
    #                 f"has no method {handler} "
    #                 f"to handle webhook on topic {topic}"
    #             )



                

    # async def handle_connections(self, data):
        # print("Estamos en el último handler !!!!!!!!!!!!!")


















