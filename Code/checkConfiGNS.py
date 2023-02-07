import os
import json
from typing import List

# Class Router


class Router:
    def __init__(self, name_folder: str, path_folder: str):
        self.name_folder = name_folder  # Nom du dossier associé à un routeur
        self.path_folder = path_folder # Chemin du dossier associé à un routeur
        self.name_file = "" # Nom du fichier de configuration associé à un routeur
        self.path_file = "" # Chemin du fichier de configuration associé à un routeur
        self.number = "" # Numero du routeur (plusieurs routeur peuvent avoir le même numéro)
        self.label = ""  # Nom du routeur dans son fichier de config

    def get_name_folder(self):
        return self.name_folder

    def get_name_file(self):
        return self.name_file
    
    def get_path_folder(self):
        return self.path_folder
    
    def get_path_file(self):
        return self.path_file

    def get_number(self):
        return self.number

    def get_label(self):
        return self.label

    def set_name_file(self, nom: str):
        self.name_file = nom
    
    def set_path_folder(self, path: str):
        self.path_folder = path
    
    def set_path_file(self, path: str):
        self.path_file = path
    
    def set_number(self, number: str):
        self.number = number

    def set_label(self, label: str):
        self.label = label


# Affichage de tous les routeurs du projet
def affichage_router(liste: List[Router]):
    for router in liste:
        print(router.get_name_folder(), "_",
              router.get_name_file(), "_",
              router.get_number())

# Création du JSON de correspondance dossier-routeur


def creation_json(liste: List[Router], name_project: str):
    data = []
    # ouvre un fichier en mode écriture
    with open('Correspondance/' + name_project + '.json', 'w') as f:
        # écrit le contenu de la liste dans le fichier au format JSON
        for router in liste:
            data.append({
                "name_folder": router.get_name_folder(),
                "path_folder": router.get_path_folder(),
                "name_file": router.get_name_file(),
                "path_file": router.get_path_file(),
                "number_router": router.get_number(),
                "label_router": router.get_label()
            })
        f.write(json.dumps(data, separators=(',', ':'), indent=4))


# Création des variables
liste_router: List[Router] = []
name_project: str = "project_type"

# Spécifie le chemin absolu du dossier à lister
folder_path = 'C:/Users/colin/GNS3/projects/' + name_project + '/project-files/dynamips'
router_path = '/configs'

# Obtient la liste de tous les fichiers et dossiers dans le dossier
items = os.listdir(folder_path)

# Parcourt la liste et créer les routeurs
for item in items:
    # Utilise le chemin absolu pour construire le chemin complet de l'élément
    item_path = os.path.join(folder_path, item)
    if os.path.isdir(item_path):
        liste_router.append(Router(item, folder_path)) # Création d'un routeur avec seulement un nom de dossier

# Parcourt la liste des routeurs et récupére les infos nécessaire (name_file, numero, label)
for router in liste_router:
    path_file_configuration = folder_path+'/'+router.get_name_folder()+router_path
    name_files = os.listdir(path_file_configuration)
    for name_file in name_files:
        if (name_file[3:17] == "startup-config" or name_file[4:18] == "startup-config"):
            router.set_name_file(name_file) # Ajout nom du fichier de configuration du routeur
            router.set_number(name_file[1]) # Ajout nom du numero du routeur
            router.set_path_file(path_file_configuration) # Ajout du chemin du fichier de configuration

            # Recherche du nom du routeur dans le fichier de configuration existant
            with open(path_file_configuration+'/'+name_file, "r") as f:
                for line in f:
                    words = line.split()
                    if "hostname" in words:
                        name_router = words[words.index("hostname")+1]
                        router.set_label(name_router) # Ajout nom du routeur


# Affichage
# affichage_router(liste_router)

# Création fichier JSON de l'organisation du projet gns3
creation_json(liste_router, name_project)
