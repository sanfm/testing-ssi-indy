import aiohttp
import asyncio
import os
import time

from modulos import utils
from modulos.peticiones import Peticion
from modulos.hookclass import WebHook




class webhook_handler:


    def __init__(self, peticion, timer, max_iter):
        self.peticion = peticion
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

            await self.peticion.get_cred_id()






    async def estado_prueba(self, notif):

        if self.first_iter:
            self.timer.start()
            self.first_iter = False


        await self.peticion.enviar_prueba(notif)

        if notif.get("state") == "done":
            self.contador += 1

            if self.contador % 10 == 0:
                print(f"######## Verificadas {self.contador} de {self.max_iter} credenciales")

            if self.contador == self.max_iter:
                self.timer.stop()
                avg = self.timer.duration / self.max_iter
                utils.log_msg(f"Tiempo medio en verificar una credencial: {avg}")
                self.contador = 0
                self.first_iter = True




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

    hook_handler = webhook_handler(peticion, timer, n_iteraciones)

    hook = WebHook(webhook_port, hook_handler)

    # iniciar servidor a la escucha de eventos
    await hook.webhook_server_init()


    aceptar_invit = None




    utils.log_status("Introducir detalles de la invitacion")
    conexion = await peticion.recibir_invitacion()
    con_id = conexion.get("connection_id")
    aceptar_invit = await peticion.aceptar_invitacion(con_id)




    options = "1) Input New Invitation\n" "2) send cred proposal\n" "3) send request\n" "4) store credential\n" "5) enviar presentation proof\n"
    async for option in utils.prompt_loop(options):

        if option is not None:
            option = option.strip()

        if option is None or option in "xX":
            break

        elif option == "1":
            utils.log_status("Introducir detalles de la invitacion")
            conexion = await peticion.recibir_invitacion()
            con_id = conexion.get("connection_id")

            # Aceptar la inviation
            aceptar_invit = await peticion.aceptar_invitacion(con_id)


        elif option == "2":
            # send proposal
            await peticion.enviar_propuesta_cred(con_id)

        elif option == "3":
            cred_ex_id = input("introducir cred_ex_id: ")
            await peticion.enviar_peticion_cred(cred_ex_id)

        elif option == "4":
            cred_ex_id = input("introducir cred_ex_id: ")
            await peticion.almacenar_credencial(cred_ex_id)

        elif option == "5":
           pres_ex_id = input("introducir pres_ex_id: ")
            await peticion.enviar_presentacion_prueba(pres_ex_id)



    await terminar(peticion, hook)
    



            





webhook_port = 12001
admin_api = 'http://0.0.0.0:12000'
n_iteraciones = 100

asyncio.run(main()) 
