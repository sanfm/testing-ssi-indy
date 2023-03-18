import aiohttp
import asyncio
import os

from modulos import utils
from modulos.peticiones import Peticion
from modulos.hookclass import WebHook




class webhook_handler:


    def __init__(self, peticion, role, timer, max_iter):
        self.peticion = peticion
        self.role = role
        self.timer = timer
        self.max_iter = max_iter
        self.contador = 0
        self.first_iter = True



    async def estado_conexion(self, notif):
        print("-"*40)
        print(f"estado conexion: {notif.get('state')}")
        print("-"*40)
        if notif.get("state") == 'completed':
            con_id = notif.get("connection_id")
            print(f"connection_id: {con_id}")

            print("-"*40)
            print("Enviando propuesta credencial")
            print("-"*40)
            # Enviar propuesta credencial
            await self.peticion.enviar_propuesta_cred(con_id)



    async def emitir_credencial(self, notif):

        await self.peticion.expedir_credencial(notif)



        if notif.get("state") == "done":
            print("-"*40)
            print("credencial expedido")
            print("-"*40)

            # Una vez expedida la credencial --> issuer solicita prueba
            if self.role == 'verifier_escenario_3':
                escenario_3 = True
            else:
                escenario_3 = False
            print('Comenzando bucle de verificacion de credenciales')
            self.timer.start()
            for i in range(self.max_iter):
                await self.peticion.enviar_peticion_prueba(notif.get('connection_id'), escenario_3)






    async def estado_prueba(self, notif):

        await self.peticion.enviar_prueba(notif)

        if notif.get("state") == "done":
            self.contador += 1

            if self.contador % 10 == 0:
                print(f"######## Verificadas {self.contador} de {self.max_iter} credenciales")

            if self.contador == self.max_iter:
                self.timer.stop()
                avg = self.timer.duration / self.max_iter
                utils.log_msg(f"Tiempo medio en verificar una credencial: {avg}")






async def terminar(peticion, hook):
    await peticion.terminar_sesion()
    await hook.webhook_server_terminate()
    os._exit(1)


async def crear_schema(peticion):
    nombre = 'titulo-uni'
    version = "1.0"
    atributos = [
            "nombre",
            "fecha",
            "grado",
            "edad"
            ]
    tag = "tituloUniversidad"
    await peticion.registrar_schema_y_creddef(nombre, version, atributos, tag)





async def main():


    # iniciar peticiones
    peticion = Peticion(admin_api)



    n_iteraciones = int(input("Introducir numero de iteraciones: "))

    timer = utils.log_timer(f"se han verificado {n_iteraciones} credenciales en: ")


    hook_handler = webhook_handler(peticion, agent_role, timer, n_iteraciones)

    hook = WebHook(webhook_port, hook_handler, agent_role)

    # iniciar servidor a la escucha de eventos
    await hook.webhook_server_init()



    # Comprobar si ya existe el esquema la cred def (sino crearlas):
    await peticion.get_creddef()




    # Generar invitacion:
    invit = await peticion.crear_invitacion()
    print('invitation URL:')
    print(invit.get("invitation_url"))




    options = "1) Generar nueva invitacion\n" "2) generar esquema\n" "3) enviar oferta\n" "4) enviar credencial\n" "5) comprobar si existe cred_def\n" "6) enviar proof request\n" "7) verificar prueba\n"
    async for option in utils.prompt_loop(options):

        if option is not None:
            option = option.strip()

        if option is None or option in "xX":
            break

        elif option == "1":
            invit = await peticion.crear_invitacion()
            print('invitation URL:')
            print(invit.get("invitation_url"))

        elif option == "2":
            await crear_schema(peticion)

        elif option == "3":
            con_id = input("introducir con_id: ")
            await peticion.enviar_oferta_cred(con_id)

        elif option == "4":
           cred_ex_id = input("introducir cred_ex_id: ")
            await peticion.enviar_credencial(cred_ex_id)
    
        elif option == "5":
            # comprobar si ya se ha creado la cred_def
            await peticion.get_creddef()

        elif option == "6":
            con_id = input("introducir con_id: ")
            await peticion.enviar_peticion_prueba(con_id)

        elif option == "7":
            pres_ex_id = input("introducir pres_ex_id: ")
            await peticion.verificar_prueba(pres_ex_id)
    
    await terminar(peticion, hook)
    







webhook_port = 11001
admin_api = 'http://localhost:11000'
agent_role = 'verifier_escenario_3'
n_iteraciones = 100

asyncio.run(main()) 
