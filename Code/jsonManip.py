import json
import os

# Récupération des données
def get_data_from_json(name_json):
    # ouvrir le fichier JSON
    if os.path.exists(name_json):
        with open(name_json, "r") as json_file:
            data = json.load(json_file)
        return data
    else:
        print("le fichier test.json n'existe pas")

configuration = get_data_from_json("JSON/test.json")
print("Configuration actuelle : \n"+json.dumps(configuration, indent=2))

rname=input("Nom du Routeur : ")
rnum=input("Numero du Routeur : ")
ok="o"
interfaces=[]
while ok == "o" :
    print("ajout d'une interface : \n")
    iname=input("nom de l'interface : ")
    iIp=input("adresse ip : ")
    iMask=input("Masque : ")
    interface={
                    "name": iname,
                    "ip": iIp,
                    "mask": iMask
                }
    interfaces.append(interface)
    ok=input("voulez vous ajouter une autre interface o/n : ")
bgpconfig=input("souhaitez vous configurer BGP o/n : ")
if bgpconfig == "o":
    ASnum=input("numero d'AS : ")
    neighbors=[]
    ok = input("ajouter un nouveau voisin ? o/n :")
    while ok == "o" :
        neighbors.append(input("numero du voisin : "))
        print("les voisins sont : "+str(neighbors)+"\n")
        ok = input("ajouter un nouveau voisin ? o/n :")
    newRouteur={
        "name": rname,
        "numero": rnum,
        "interface": interfaces,
        "bgpConfig": {
            "ASnumber": ASnum,
            "neighbors": neighbors
        }
    }
else :
    newRouteur={
        "name": rname,
        "numero": rnum,
        "interface": interfaces,
    }

configuration["routers"].append(newRouteur)
with open("JSON/test.json", "w") as json_file: 
    json.dump(configuration,json_file,indent=4)
