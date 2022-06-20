import requests


admin_api = 'htpp://0.0.0.0:11000'


resp = requests.post(f"{admin_api}/connections/create-invitation")

print(resp.json())
