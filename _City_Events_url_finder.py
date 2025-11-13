# Pour extraire tous les url :
import requests
from bs4 import BeautifulSoup

response = requests.get("https://www.jds.fr/")
content_html = response.text
soup = BeautifulSoup(content_html, "html.parser")
# with open("_City_Events_url_finder.html", "w") as file:
#     file.write(response.text)


def all_cities(content):
    city_links = set()
    for a_tag in soup.find_all("a", class_="text-white text-uppercase", href=True):
        href = a_tag["href"]
        if "https://www.jds.fr/" in href and "=200" not in href:
            city_links.add(href)
    city_links = list(city_links)
    return city_links


city_links = all_cities(all_cities)
print(f"Nombre de liens : {len(city_links)}")
print(f"Liste de liens : {city_links}")
