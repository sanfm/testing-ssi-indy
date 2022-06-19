import requests


admin_api = 'http://0.0.0.0:11000'


#  Crear una invitación
invitation  =  requests.post(f"{admin_api}/connections/create-invitation")

print(invitation.json())



