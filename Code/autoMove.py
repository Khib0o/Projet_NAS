import os
import json
import sys
import shutil

# Récupération des données de la configuration du projet gns3
def get_data_from_json(name_json):
    # ouvrir le fichier JSON
    if os.path.exists(name_json):
        with open(name_json, "r") as json_file:
            data = json.load(json_file)
        return data
    else:
        print("le fichier test.json n'existe pas")


# Récupération de la configuration du projet GNS3
configuration_gns3 = get_data_from_json("Correspondance/test.json")

# Initialisation des constancte
path_folder = "Configuration"

# Vérification avant déplacement
counter_file = 0
counter_router = 0
# Récupération nombre de fichier de configuration
for name_file in os.listdir(path_folder):
    if os.path.isfile(os.path.join(path_folder, name_file)):
        counter_file += 1
# Récupération nombre de routeur
for router in configuration_gns3:
    counter_router += 1
# Vérification si tous les fichier de configurations existe avant déplacement
if counter_router == counter_file:
    for name_file in os.listdir(path_folder):
        if os.path.isfile(os.path.join(path_folder, name_file)):
            find = False
            for router in configuration_gns3:
                if router["name_file"] == name_file:
                    find = True
            if not find:
                print("Erreur tous les fichier de destination n'existe pas ")
                sys.exit()
else:
    print("Erreur nombre de routeurs différents à la destination ")
    sys.exit()

# Déplacement des fichiers de configurations
for name_file in os.listdir(path_folder):
    if os.path.isfile(os.path.join(path_folder, name_file)):
        print("Déplacement de : " + name_file)
        for router in configuration_gns3:
            # Recherche du nom du routeur dans le fichier de configuration existant
            find = False
            with open(path_folder+'/'+name_file, "r") as f:
                for line in f:
                    words = line.split()
                    if "hostname" in words:
                        name_router = words[words.index("hostname")+1]
                        if router["label_router"] == name_router and router["name_file"] == name_file:
                            print("Trouvé")
                            find = True
            if find:
                # os.replace(path_folder+'/'+name_file, router["path_file"]+'/'+name_file)
                shutil.copy(path_folder+'/'+name_file, router["path_file"]+'/'+name_file)
