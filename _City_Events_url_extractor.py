import requests
from bs4 import BeautifulSoup
import time
import re
import os

# ==================== PARTIE 1 : EXTRACTION DES URLs DES VILLES ====================
print("="*60)
print("ÉTAPE 1 : Extraction des URLs des villes")
print("="*60)

response = requests.get("https://www.jds.fr/")
content_html = response.text
soup = BeautifulSoup(content_html, "html.parser")

# with open("url_finder.html", "w", encoding="utf-8") as file:
#     file.write(response.text)
# print("✓ Fichier url_finder.html créé")


def all_cities(soup):
    city_links = set()
    for a_tag in soup.find_all("a", class_="text-white text-uppercase", href=True):
        href = a_tag["href"]
        if "https://www.jds.fr/" in href and "=200" not in href:
            # Ajouter /agenda/ si pas déjà présent
            if not href.endswith('/agenda/'):
                if href.endswith('/'):
                    href += 'agenda/'
                else:
                    href += '/agenda/'
            city_links.add(href)
    return list(city_links)


city_links = all_cities(soup)
print(f"\n✓ {len(city_links)} villes trouvées")


# ==================== PARTIE 2 : TÉLÉCHARGEMENT DES PAGES ====================
print(f"\n{'='*60}")
print("ÉTAPE 2 : Téléchargement des pages pour chaque ville")
print("="*60)


def extract_city_name(url):
    """Extrait le nom de la ville depuis l'URL"""
    # Ex: https://www.jds.fr/mulhouse/agenda/ -> mulhouse
    parts = url.rstrip('/').split('/')
    # Trouver la partie après jds.fr
    for i, part in enumerate(parts):
        if part == 'www.jds.fr' or part == 'jds.fr':
            if i + 1 < len(parts):
                return parts[i + 1]
    return "unknown"


def safe_filename(city_name, page_num):
    """Crée un nom de fichier sécurisé"""
    city_name = re.sub(r'[<>:"/\\|?*]', '_', city_name)
    return f"{city_name}_page{page_num}.html"


def download_all_pages(base_url, city_name, max_attempts=1000):
    """Télécharge toutes les pages jusqu'à trouver une page vide ou sans événements"""
    downloaded = 0
    consecutive_empty = 0
    
    for page_num in range(1, max_attempts + 1):
        page_url = f"{base_url}?page={page_num}"
        filename = safe_filename(city_name, page_num)
        
        print(f"  📥 Page {page_num}...", end=" ", flush=True)
        
        try:
            response = requests.get(page_url, timeout=10)
            
            if response.status_code == 200:
                # Vérifier si la page contient des événements
                soup_page = BeautifulSoup(response.text, 'html.parser')
                events = soup_page.find_all(class_="col-12 pt-4")
                
                if events and len(events) > 0:
                    with open(filename, "w", encoding="utf-8") as file:
                        file.write(response.text)
                    print(f"✓ {filename} ({len(events)} événements)")
                    downloaded += 1
                    consecutive_empty = 0  # Réinitialiser le compteur
                else:
                    print("⊗ Aucun événement trouvé")
                    consecutive_empty += 1
                    # Arrêter après 2 pages vides consécutives
                    if consecutive_empty >= 2:
                        print(f"  → Arrêt après {consecutive_empty} pages vides consécutives")
                        break
            elif response.status_code == 404:
                print("✗ Page inexistante (404)")
                break
            else:
                print(f"✗ Erreur {response.status_code}")
                consecutive_empty += 1
                if consecutive_empty >= 2:
                    break
        
        except Exception as e:
            print(f"✗ {e}")
            consecutive_empty += 1
            if consecutive_empty >= 2:
                break
        
        time.sleep(0.5)  # Pause réduite pour aller plus vite
    
    return downloaded


total_downloaded = 0
cities_stats = []

for i, base_url in enumerate(city_links, start=1):
    # Nettoyer l'URL
    if '?' in base_url:
        base_url = base_url.split('?')[0]
    
    city_name = extract_city_name(base_url)
    
    print(f"\n{'='*60}")
    print(f"Ville {i}/{len(city_links)} : {city_name.upper()}")
    print(f"URL : {base_url}")
    print(f"{'='*60}")
    
    # Télécharger toutes les pages
    city_downloaded = download_all_pages(base_url, city_name)
    total_downloaded += city_downloaded
    
    cities_stats.append({
        'ville': city_name,
        'pages': city_downloaded
    })
    
    print(f"  ✓ {city_downloaded} page(s) téléchargée(s) pour {city_name}")
    
    # Pause entre les villes
    if i < len(city_links):
        print("⏳ Pause de 2 secondes...")
        time.sleep(2)


# ==================== RÉSUMÉ ====================
print(f"\n{'='*60}")
print("RÉSUMÉ DÉTAILLÉ")
print("="*60)
print(f"✓ {len(city_links)} villes analysées")
print(f"✓ {total_downloaded} fichiers HTML téléchargés")
print("\nDétail par ville :")
for stat in cities_stats:
    print(f"  • {stat['ville']}: {stat['pages']} page(s)")
print(f"{'='*60}")

# Lister les fichiers créés
print("\nFichiers créés :")
html_files = [f for f in os.listdir('.') if f.endswith('.html') and '_page' in f]
print(f"  {len(html_files)} fichiers trouvés")
if len(html_files) <= 20:
    for f in sorted(html_files):
        print(f"  • {f}")
