import json

# Charger le JSON depuis un fichier pour éviter les erreurs de copier-coller
with open("surfspots.json", "r", encoding="utf-8") as f:
    data = json.load(f)



# Compter les éléments
nb_elements = len(data["elements"])
print("Nombre d'éléments :", nb_elements)


