import aiohttp
import asyncio
import os

from modulos import utils
from modulos.peticiones import Peticion
from modulos.hookclass import WebHook




class webhook_handler:


    def __init__(self, peticion, timer, max_iter):
        self.peticion = peticion
        self.timer = timer
        self.max_iter = max_iter
        self.cont_issued_creds = 0
        self.first_iter = True


    async def estado_conexion(self, notif):
        print("-"*40)
        print(f"estado conexion: {notif.get('state')}")
        print("-"*40)


    async def emitir_credencial(self, notif):

        await self.peticion.expedir_credencial(notif)

        if self.first_iter:
            self.timer.start()
            self.first_iter = False


        if notif.get("state") == "done":
            self.cont_issued_creds += 1

            if self.cont_issued_creds % 10 == 0:
                print(f"######## Expedidas {self.cont_issued_creds} de {self.max_iter} credenciales")

            if self.cont_issued_creds == self.max_iter:
                self.timer.stop()
                avg = self.timer.duration / self.max_iter
                utils.log_msg(f"Tiempo medio en expedir una credencial: {avg}")
                self.cont_issued_creds = 0
                self.first_iter = True
                self.timer.reset()





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


    n_creds = int(input("Introducir numero de iteraciones: "))

    issue_timer = utils.log_timer(f"se han expedido {n_creds} credenciales en: ")


    hook_handler = webhook_handler(peticion, issue_timer, n_creds)

    hook = WebHook(webhook_port, hook_handler)

    # iniciar servidor a la escucha de eventos
    await hook.webhook_server_init()


    # comprobar si existe el esquema y la cred def (sino, crearlas):
    await peticion.get_creddef()



    # Generar invitacion
    invit = await peticion.crear_invitacion()
    print('invitacion URL:')
    print(invit.get("invitation_url"))




    options = "1) Generar nueva invitacion\n" "2) generar esquema\n" "3) enviar oferta\n" "4) enviar credencial\n"
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
    
    
    await terminar(peticion, hook)
    




webhook_port = 11001
admin_api = 'http://0.0.0.0:11000'
n_cred = 100

asyncio.run(main())
