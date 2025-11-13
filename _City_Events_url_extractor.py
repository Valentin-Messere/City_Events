# Pour extraire le html de chaque page :
import requests
import time
import re
from _City_Events_url_finder import city_links

for i, url in enumerate(city_links, start=1):
    print(f"Téléchargement {i}/{len(city_links)} : {url}")

    def safe_filename(url):
        name = url.split("/")[-2].replace(".html", "")
        name = re.sub(r'[<>:"/\\|?*]', '_', name)
        return f"{name}.html"

    city_name = safe_filename(url)
    response = requests.get(url)
    if response.status_code == 200:
        with open(city_name, "w", encoding="utf-8") as file:
            file.write(response.text)
        print(f"✓ {city_name} créé")
    else:
        print(f"✗ Erreur {response.status_code} pour {url}")
    time.sleep(1)


print("Téléchargement terminé")
