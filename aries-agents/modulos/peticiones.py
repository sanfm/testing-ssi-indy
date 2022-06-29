import aiohttp
import asyncio
import base64
import binascii
import json
from urllib.parse import urlparse

from . import utils





class Peticion:

    def __init__(self, admin_api):
        # self.session = None
        self.admin_api = admin_api
        self.session = aiohttp.ClientSession(admin_api)


    # async def iniciar_sesion():
    #     self.session = aiohttp.ClientSession()


    async def terminar_sesion(self):
        if self.session:
            await self.session.close()
            print('cerrando sesion')






    async def admin_request(
            self, method, path, data=None, text=False, params=None, headers=None
            ) -> aiohttp.ClientResponse:

        async with self.session.request(method, path, json=data, params=params, headers=headers) as response:

            resp = await response.json() 

        return resp




    async def crear_invitacion(
            self, use_did_exchange: bool = True, auto_accept: bool = True
            ):

        if use_did_exchange:
            invi_params = {"auto_accept": json.dumps(auto_accept)}
            payload = {
                    "handshake_protocols": ["rfc23"], 
                    "use_public_did": False
                    }
            invitacion = await self.admin_request('POST', '/out-of-band/create-invitation', payload, params=invi_params)

        else:
            invitacion = await self.admin_request('POST', '/connections/create-invitation')

        return invitacion




    async def recibir_invitacion(self):

        async for details in utils.prompt_loop("Detalles de la invitación: "):
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
            
            if '/out-of-band/' in details.get("@type", ""):# si está la cadena /out-of-band/ en la invitación
                # Reusar conexiones existentes si hay conexiones anteriores entre ambos agentes
                params["use_existing_connection"] = "true"
                conexion = await self.admin_request('POST', '/out-of-band/receive-invitation', details, params=params)
            else:
                conexion = await self.admin_request('POST', '/connections/receive-invitation', details, params=params)


        return conexion



    async def aceptar_invitacion(self, con_id):

        path = '/didexchange/' + con_id + '/accept-invitation'

        algo = await self.admin_request('POST', path) 

    



    async def registrar_schema_y_creddef(
            self,
            schema_name,
            schema_version,
            schema_attrs,
            tag
            ):

        schema_body = {
                "schema_name" = schema_name,
                "schema_version" = schema_version,
                "attributes" = schema_attrs
                }
        schema_response = await self.admin_request('POST', '/schemas', schema_body)
        utils.log_json(json.dumps(schema_response), label='Schema:')

        await asyncio.sleep(4.0)
        if "schema_id" in schema_response:
            schema_id = schema_response["schema_id"]
        else:
            print("Schema ¿No se ha creado correctamente?")

       utils.log_msg("Schema ID:", schema_id) 

       # crear el credential definition

       creddef_tag = tag 
       creddef_body = {
               "schema_id": schema_id,
               "tag": creddef_tag
               }
       creddef_response = await self.admin_request('POST', '/credential-definitions', creddef_body)

       await asyncio.sleep(4.0)
       if "credential_definition_id" in creddef_response:
           creddef_id = creddef_response["credential_definition_id"]
       else:
           print("creddef ¿No se ha registrado bien?")


       utils.log_msg("Cred def ID:", creddef_id) 






    async def enviar_propuesta_cred(self, con_id):
        # hay que obtener el conexion ID




    async def enviar_oferta_cred(self):




    async def enviar_peticion_cred(self):






    async def expedir_credencial(self):
        print("expedir credencial")
        await self.admin_request('POST', '')



# async def main():

#     # a ClientSession() le podemos añadir una URL_base que podemos usar
#     # en todas las peticiones posteriores: clientSession(Base_URL)
#     async with aiohttp.ClientSession(admin_api) as session:

#         invit = await crear_invitacion(session)

#         print(invit)



# admin_api = 'http://0.0.0.0:11000'


#asyncio.run(main())
