import os
import json

# Class Router
class Router:
    def __init__(self, nom, numero, label):
        self.nom = nom
        self.numero = numero
        self.label = label

    def getNom(self):
        return self.nom

    def getNumero(self):
        return self.numero

    def getLabel(self):
        return self.label

    def setNumero(self, numero):
        self.numero = numero

    def setLabel(self, label):
        self.label = label


def affichageRouter(liste):  # you can add variables to the function
    for router in liste:
        print(router.getNom(), "_", router.getNumero())


def creationJSON(liste, nameProject):
    data = []
    # ouvre un fichier en mode écriture
    with open('Correspondance/'+ nameProject +'.json', 'w') as f:
        # écrit le contenu de la liste dans le fichier au format JSON
        for router in liste:
            data.append({
                "nom": router.getNom(),
                "numero": router.getNumero(),
                "label": router.getLabel()
            })
        f.write(json.dumps(data, separators=(',', ':')))


listeRouter = []
nameProject = "test"

# Spécifie le chemin absolu du dossier à lister
folder_path = 'C:/Users/colin/GNS3/projects/'+ nameProject +'/project-files/dynamips'

# Obtient la liste de tous les fichiers et dossiers dans le dossier
items = os.listdir(folder_path)

# Parcourt la liste et affiche seulement les noms de dossiers
for item in items:
    # utilise le chemin absolu pour construire le chemin complet de l'élément
    item_path = os.path.join(folder_path, item)
    if os.path.isdir(item_path):
        listeRouter.append(Router(item, 0, ""))

router_path = '/configs'

for router in listeRouter:
    numeros = os.listdir(folder_path+'/'+router.getNom()+router_path)
    for numero in numeros:
        router.setNumero(numero[1])

affichageRouter(listeRouter)

creationJSON(listeRouter, nameProject)
