from bs4 import BeautifulSoup
import os


def clean_name(name):
    name = name.replace("\xa0", " ")
    name = name.replace("Que faire à ", "")
    name = name.replace(" ?", "")
    name = " ".join(name.split())
    return name


data = []
erreurs = 0
avertissements = 0

for file in os.listdir():
    if file.endswith(".html"):
        print(f"Lecture de {file}...")
        with open(file, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
            city_name = soup.find("h1")

            if city_name:
                city_name = clean_name(city_name.text.strip())
            
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
                        "description": info_text[0].text.strip(),
                        "lien": info_a[3].get('href', '') if len(info_a) > 3 else "",
                    })
                    
                except Exception as e:
                    print(f"  ❌ Erreur événement {idx+1}: {e}")
                    erreurs += 1
                    continue

print(f"\n{'='*60}")
print("Extraction terminée :")
print(f"  ✓ {len(data)} événements extraits")
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
            file.write(f"{data[i]['lien']};")
            if i < len(data) - 1:
                file.write("\n")
    
    print(f"\n✓ Fichier CSV créé avec {len(data)} événements")
else:
    print("\n❌ Aucun événement extrait")
