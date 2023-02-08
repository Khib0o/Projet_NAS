from src.parseur import *
from src.classes import *
from src.gns_api import *

from os import system
from os import path

system('clear')
while (True) : 
    prompt = "Bonjour, que voulez vous faire (1-4) :\n"
    prompt += "1) Extraire la table de routage des fichiers d'un projet GNS3\n"
    prompt += "2) Générer les fichiers config à partir de conf.json\n"
    prompt += "3) Push les fichiers générés dans le projet GNS3\n"
    prompt += "4) Quitter"
    
    
    print(prompt)

    ans = input()
    match ans:

        case "1":
            print("Veuillez entrer le nom du projet GNS : ")
            name = input()
            print("Extraction de la table de routage des fichiers du projet GNS...")
            generateFileRoutingTable(name)
            
            print("Extraction terminée")
            
        case "2":
            print("Génération des fichiers de configurations dans le répertoire ./configs")
            pars = Parseur("conf.json")
            network = Network(pars)
            network.generateIPAdresses()
            network.giveNeighborsToRouters()
            network.setupVrfOfPe()
            
            if not path.exists("configs/"):
                system('mkdir configs')
            
            network.genAllConfigFiles("configs/")
            print("Génération finalisée")   
                             
        case "3":
            print("Pushing des fichiers vers le projet GNS...")
            pushConfigToProject()
            print("Pushing réalisé sans erreur")
            
        case _:
            exit(0)
            
    print("\n\n\n")