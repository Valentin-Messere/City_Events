from bs4 import BeautifulSoup
import os


def clean_name(name):
    name = name.replace("\xa0", " ")
    name = name.replace(" : Agenda et événements", "")
    name = " ".join(name.split())
    return name


def clean_description(text):
    """
    Nettoie la description pour qu'elle tienne sur une seule ligne (sans \n, \t, espaces multiples…)
    """
    text = text.replace("\xa0", " ").replace("&nbsp;", " ")
    return " ".join(text.split())


def extract_city_from_filename(filename):
    """
    Extrait le nom de la ville depuis le nom du fichier (ex: paris_page28.html -> paris)
    """
    # Retirer l'extension .html
    name = filename.replace(".html", "")
    
    # Extraire la partie avant _page
    if "_page" in name:
        city = name.split("_page")[0]
    else:
        city = name
    
    return city.lower()


def get_all_cities_from_files():
    """
    Récupère la liste de toutes les villes présentes dans les noms de fichiers
    """
    cities = set()
    for file in os.listdir():
        if file.endswith(".html"):
            city = extract_city_from_filename(file)
            cities.add(city)
    return cities


def is_valid_city(h1_name, valid_cities):
    """
    Vérifie si le nom du h1 correspond à une ville valide (présente dans les fichiers)
    """
    if not h1_name:
        return False
    
    # Normaliser le nom du h1 pour la comparaison
    h1_normalized = h1_name.lower().strip()
    
    # Vérifier si une des villes valides est contenue dans le h1
    # (car le h1 peut contenir "Paris" ou "Paris : Agenda et événements")
    for city in valid_cities:
        if city in h1_normalized:
            return True
    
    return False


data = []
erreurs = 0
avertissements = 0
villes_rejetees = 0

# Récupérer la liste de toutes les villes présentes dans les fichiers
valid_cities = get_all_cities_from_files()
print(f"Villes détectées dans les fichiers : {', '.join(sorted(valid_cities))}\n")

for file in os.listdir():
    if file.endswith(".html"):
        print(f"Lecture de {file}...")
        with open(file, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
            city_name_h1 = soup.find("h1")

            if city_name_h1:
                city_name = clean_name(city_name_h1.text.strip())
            else:
                city_name = None
            
            # Vérifier si le h1 correspond à une vraie ville (présente dans les fichiers)
            if not is_valid_city(city_name, valid_cities):
                print(f"  ⊘ '{city_name}' rejeté (pas dans la liste des villes)")
                villes_rejetees += 1
                continue
            
            infos = soup.find_all(class_="col-12 pt-4")
            print(f"  → {len(infos)} événements trouvés")
            
            for idx, info in enumerate(infos):
                try:
                    info_a = info.find_all("a")
                    info_span = info.find_all("span")
                    info_text = info.find_all(class_="d-block description font-size-14 lh-sm")
                    
                    # Extraction de l'image (URL seulement)
                    img = info.find("img")
                    img_url = ""
                    if img:
                        img_url = img.get('src', '') or img.get('data-src', '') or img.get('data-lazy-src', '')
                    
                    # Vérification minimale
                    if len(info_span) < 2 or len(info_text) < 1:
                        print(f"  ❌ Événement {idx+1}: éléments essentiels manquants")
                        erreurs += 1
                        continue
                    
                    # Avertissements
                    warnings = []
                    if not img_url:
                        warnings.append("image")
                    if len(info_a) < 4:
                        warnings.append("lien billets")
                    
                    if warnings:
                        print(f"  ⚠️  Événement {idx+1}: {', '.join(warnings)} manquant(s)")
                        avertissements += 1

                    data.append({
                        "ville": city_name if city_name else "Inconnu",
                        "image_url": img_url,
                        "spectacle": info_a[0].text.strip() if len(info_a) > 0 else "",
                        "nom": info_span[0].text.strip(),
                        "page": info_a[1].get('href', '') if len(info_a) > 1 else "",
                        "date": info_span[1].text.strip(),
                        "localisation": info_a[2].text.strip() if len(info_a) > 2 else "",
                        "description": clean_description(info_text[0].text),
                        "lien": info_a[3].get('href', '') if len(info_a) > 3 else "",
                    })
                    
                except Exception as e:
                    print(f"  ❌ Erreur événement {idx+1}: {e}")
                    erreurs += 1
                    continue

print(f"\n{'='*60}")
print("Extraction terminée :")
print(f"  ✓ {len(data)} événements extraits")
print(f"  ⊘ {villes_rejetees} fichiers rejetés (catégories)")
print(f"  ⚠️  {avertissements} événements avec infos manquantes")
print(f"  ❌ {erreurs} événements ignorés")
print(f"{'='*60}")


if len(data) > 0:
    with open("_City_Events_data.csv", "w", encoding="utf-8") as file:
        file.write("Ville;Image_URL;Spectacle;Nom;Page;Date;Localisation;Description;Lien_Billets\n")
        
        for i in range(len(data)):
            file.write(f"{data[i]['ville']};")
            file.write(f"{data[i]['image_url']};")
            file.write(f"{data[i]['spectacle']};")
            file.write(f"{data[i]['nom']};")
            file.write(f"{data[i]['page']};")
            file.write(f"{data[i]['date']};")
            file.write(f"{data[i]['localisation']};")
            file.write(f"{data[i]['description']};")
            file.write(f"{data[i]['lien']}")
            if i < len(data) - 1:
                file.write("\n")
    
    print(f"\n✓ Fichier CSV créé avec {len(data)} événements")
else:
    print("\n❌ Aucun événement extrait")
