import aiohttp
import asyncio
import base64
import binascii
import json
from urllib.parse import urlparse

import utils





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




async def recibir_invitacion(
        session
        ):

    async for details in prompt_loop("Detalles de la invitación: "):
        b64_invite = None
        try:
            url = urlparse(details)
            query = url.query
            if query and "c_i=" in query:
                pos = query.index("c_i=") + 4
                b64_invite = query[pos:]
            elif query and "oob=" in query:
                pos = query.index("oob=") + 4
                b64_invite = query[pos:]
            else:
                b64_invite = details
        except ValueError:
            b64_invite = details

        if b64_invite:
            try:
                padlen = 4 - len(b64_invite) % 4
                if padlen <= 2:
                    b64_invite += "=" * padlen
                invite_json = base64.urlsafe_b64decode(b64_invite)
                details = invite_json.decode("utf-8")
            except binascii.Error:
                pass
            except UnicodeDecodeError:
                pass

        if details:
            try:
                details = json.loads(details)
                break
            except json.JSONDecodeError as e:
                utils.log_msg("Invalid invitation:", str(e))


    params={}
    with utils.log_timer("Connect duration:"):
        #connection = await agent_container.input_invitation(details, wait=True)
        
        if '/out-of-band/' in invitacion_test:# si está la cadena /out-of-band/ en la invitación
            # Reusar conexiones existentes si hay conexiones anteriores entre ambos agentes
            params["use_existing_connection"] = "true"
            conexion = await admin_request(session, 'POST', '/out-of-band/receive-invitation', details, params=params)
        else:
            conexion = await admin_request(session, 'POST', '/connections/receive-invitation', details, params=params)


    return conexion

    



# async def main():

#     # a ClientSession() le podemos añadir una URL_base que podemos usar
#     # en todas las peticiones posteriores: clientSession(Base_URL)
#     async with aiohttp.ClientSession(admin_api) as session:

#         invit = await crear_invitacion(session)

#         print(invit)



# admin_api = 'http://0.0.0.0:11000'


#asyncio.run(main())
