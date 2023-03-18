import aiohttp
import asyncio
import base64
import binascii
import json
from urllib.parse import urlparse
from datetime import datetime
import time

from . import utils





class Peticion:

    def __init__(self, admin_api):
        self.admin_api = admin_api
        self.session = aiohttp.ClientSession(admin_api)
        self.cred_id = None




    async def terminar_sesion(self):
        if self.session:
            await self.session.close()
            print('cerrando sesion')






    async def admin_request(
            self, method, path, data=None, text=False, params=None, headers=None, respuesta=True
            ) -> aiohttp.ClientResponse:



        async with self.session.request(method, path, json=data, params=params, headers=headers) as response:

            if respuesta:
                resp = await response.json()
            else:
                resp = 1

        return resp



    async def get_cred_id(self):
        credentials = await self.admin_request('GET', '/credentials')
        credencial = credentials.get('results')[0]
        cred_id = credencial.get("referent")
        self.cred_id = cred_id
        print(f"cred_id: {cred_id}")



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

        async for details in utils.prompt_loop("Detalles de la invitacion: "):
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
            
            if '/out-of-band/' in details.get("@type", ""):
                # Reusar conexiones existentes si hay conexiones anteriores entre ambos agentes
                params["use_existing_connection"] = "true"
                conexion = await self.admin_request('POST', '/out-of-band/receive-invitation', details, params=params)
            else:
                conexion = await self.admin_request('POST', '/connections/receive-invitation', details, params=params)


        return conexion



    async def aceptar_invitacion(self, con_id):

        path = '/didexchange/' + con_id + '/accept-invitation'

        aceptar_invit = await self.admin_request('POST', path) 

        return aceptar_invit

    



    async def get_creddef(self):
        cred_def = await self.admin_request('GET', '/credential-definitions/created', 
                {"isser_did": "XXFm7jVVMEV6UhKifRNDEx"})
        comprobar = cred_def.get("credential_definition_ids")
        if comprobar:
            utils.log_msg("Ya existe la credential definition y el credential definition y el esquema")
        else:
            utils.log_msg("Creando esquema y Credential definition")
            nombre = "titulo-uni"
            version = "1.0"
            atributos = [
                "nombre",
                "fecha",
                "grado",
                "edad"
            ]
            tag = "tituloUniversidad"

            await self.registrar_schema_y_creddef(nombre, version, atributos, tag)
        




    async def registrar_schema_y_creddef(
            self,
            schema_name,
            schema_version,
            schema_attrs,
            tag
            ):

        schema_body = {
                "schema_name": schema_name,
                "schema_version": schema_version,
                "attributes": schema_attrs
                }
        schema_response = await self.admin_request('POST', '/schemas', schema_body)
        utils.log_json(json.dumps(schema_response), label='Schema:')

        await asyncio.sleep(4.0)
        if "schema_id" in schema_response:
            schema_id = schema_response["schema_id"]
        else:
            print("Schema: No se ha creado correctamente")

        utils.log_msg("Schema ID:", schema_id)

       # crear el credential definition

        creddef_tag = tag 
        creddef_body = {
            "revocation_registry_size": 1000,
            "schema_id": schema_id,
            "support_revocation": True,
            "tag": creddef_tag
        }
        creddef_response = await self.admin_request('POST', '/credential-definitions', creddef_body)

        await asyncio.sleep(4.0)
        if "credential_definition_id" in creddef_response:
           creddef_id = creddef_response["credential_definition_id"]
        else:
           print("creddef: No se ha registrado bien")


        utils.log_msg("Cred def ID:", creddef_id) 






    async def enviar_propuesta_cred(self, con_id):
        fecha = datetime.now()
        fecha = fecha.strftime("%Y-%m-%d %H:%M:%S:%f")
        proposal_body = {
                "auto_remove": True,
                "connection_id": con_id,
                "credential_preview": {
                    "@type": "issue-credential/2.0/credential-preview",
                    "attributes": [
                    {
                        "name": "nombre", 
                        "value": "Fede"
                    },
                    {
                        "name": "fecha", 
                        "value": fecha
                    },
                    {
                        "name": "grado", 
                        "value": "Master Ciberseguridad"
                    },
                    {
                        "name": "edad",
                        "value": "22"
                    }
                ]
                },
                "filter": {
                    "indy": {
                        "cred_def_id": "XXFm7jVVMEV6UhKifRNDEx:3:CL:8:tituloUniversidad",
                        "issuer_did": "XXFm7jVVMEV6UhKifRNDEx",
                        "schema_id": "XXFm7jVVMEV6UhKifRNDEx:2:titulo-uni:1.0",
                        "schema_issuer_did": "XXFm7jVVMEV6UhKifRNDEx",
                        "schema_name": "titulo-uni",
                        "schema_version": "1.0"
                    }
                },
                "trace": False
        }

        await self.admin_request('POST', '/issue-credential-2.0/send-proposal', proposal_body)





    async def expedir_credencial(self, notif):

        state = notif.get('state')
        con_id = notif.get('connection_id')
        cred_ex_id = notif.get('cred_ex_id')

        resultado = 0

        if state == 'proposal-received':
            # issuer contesta con una oferta send-offer
            await self.enviar_oferta_cred(con_id)
        elif state == 'offer-received':
            # holder contesta con una propuesta send-request
            await self.enviar_peticion_cred(cred_ex_id)
        elif state== 'request-received':
            # issuer expide la credencial
            await self.enviar_credencial(cred_ex_id)
        elif state == 'credential-received':
            # holder ha recibido la credencial 
            await self.almacenar_credencial(cred_ex_id)
        elif state == 'done':
            resultado = 1
            # issuer ha recibido un ack indicando que el holder ha recibido la credencial
        else:
            print("-"*40)
            print(f"estado de la credencial: {state}")
            print("-"*40)

        return resultado







    async def enviar_oferta_cred(self, con_id):
        fecha = datetime.now()
        fecha = fecha.strftime("%Y-%m-%d %H:%M:%S:%f")

        offer_request = {
                "auto_issue": False,
                "auto_remove": True,
                "connection_id": con_id,
                "credential_preview": {
                    "@type": "issue-credential/2.0/credential-preview",
                    "attributes": [
                    {
                        "name": "nombre", 
                        "value": "Fede"
                    },
                    {
                        "name": "fecha", 
                        "value": fecha
                    },
                    {
                        "name": "grado", 
                        "value": "Master Ciberseguridad"
                    },
                    {
                        "name": "edad",
                        "value": "22"
                    }
                ]
                },
                "filter": {
                    "indy": {
                        "cred_def_id": "XXFm7jVVMEV6UhKifRNDEx:3:CL:8:tituloUniversidad",
                        "issuer_did": "XXFm7jVVMEV6UhKifRNDEx",
                        "schema_id": "XXFm7jVVMEV6UhKifRNDEx:2:titulo-uni:1.0",
                        "schema_issuer_did": "XXFm7jVVMEV6UhKifRNDEx",
                        "schema_name": "titulo-uni",
                        "schema_version": "1.0"
                    }
                },
                "trace": False
        }

        await self.admin_request('POST', '/issue-credential-2.0/send-offer', offer_request)




    async def enviar_peticion_cred(self, cred_ex_id):
        await self.admin_request('POST', f'/issue-credential-2.0/records/{cred_ex_id}/send-request')



    async def enviar_credencial(self, cred_ex_id):
        await self.admin_request('POST', f'/issue-credential-2.0/records/{cred_ex_id}/issue', 
                {"comment": f"issuing credential, cred_ex_id: {cred_ex_id}"}
                )


    
    async def almacenar_credencial(self, cred_ex_id):
        await self.admin_request('POST', f'/issue-credential-2.0/records/{cred_ex_id}/store')





    
    async def enviar_peticion_prueba(self, con_id, escenario_3=False):

        if escenario_3:
            proof_request = {
                "connection_id": con_id,
                "presentation_request": {
                    "indy": {
                        "name": "Proof request",
                        "non_revoked": {
                            "to": int(time.time() - 1)
                        },
                        "requested_attributes": {
                            "0_name_uuid": {
                                "name": "nombre",
                                "non_revoked": {
                                    "to": int(time.time() - 1)
                                },
                                "restrictions": [
                                    {
                                        "schema_name": "titulo-uni"
                                    }
                                ]
                            }
                        },
                        "requested_predicates": {
                            "0_edad_uuid": {
                                "name": "edad",
                                "non_revoked": {
                                    "to": int(time.time() - 1)
                                },
                                "p_type": ">=",
                                "p_value": 18,
                                "restrictions": [
                                    {
                                        "schema_name": "titulo-uni"
                                    }
                                ]
                            }
                        },
                        "version": "1.0"
                    }
                },
                "trace": False
            }

        else:
            proof_request = {
                "connection_id": con_id,
                "presentation_request": {
                    "indy": {
                        "name": "Proof request",
                        "requested_attributes": {
                            "0_name_uuid": {
                                "name": "nombre",
                                "restrictions": [
                                    {
                                        "schema_name": "titulo-uni"
                                    }
                                ]
                            }
                        },
                        "requested_predicates": {
                            "0_edad_uuid": {
                                "name": "edad",
                                "p_type": ">=",
                                "p_value": 18,
                                "restrictions": [
                                    {
                                        "schema_name": "titulo-uni"
                                    }
                                ]
                            }
                        },
                        "version": "1.0"
                    }
                },
                "trace": False
            }


        await self.admin_request('POST', '/present-proof-2.0/send-request', proof_request)




    async def enviar_prueba(self, notif):
        state = notif.get('state')
        pres_ex_id = notif.get('pres_ex_id')
        result = 0

        if state == "request-received":
            await self.enviar_presentacion_prueba(pres_ex_id)

        elif state == "presentation-received":
            await self.verificar_prueba(pres_ex_id)

        elif state == "done":
            result = 1

        return result



    async def enviar_presentacion_prueba(self, pres_ex_id):

        presentation = {
            "indy": {
                "requested_attributes": {
                    "0_name_uuid": {
                        "cred_id": self.cred_id,
                        "revealed": True
                    }
                },
                "requested_predicates": {
                    "0_edad_uuid": {
                        "cred_id": self.cred_id 
                    }
                },
                "self_attested_attributes": {}
            }
        }

        await self.admin_request('POST', f'/present-proof-2.0/records/{pres_ex_id}/send-presentation', presentation)



    
    async def verificar_prueba(self, pres_ex_id):

        verificacion = await self.admin_request('POST', f"/present-proof-2.0/records/{pres_ex_id}/verify-presentation")

        # print("-"*40)
        # print(f"verificacion: {verificacion}")
        # print("-"*40)
