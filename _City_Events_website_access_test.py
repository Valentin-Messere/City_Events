# Pour verifier si l'accès au site marche :
import requests
response = requests.get("https://www.jds.fr/")
print(response.content)
print()
print(f"Status code : {response.status_code}")
