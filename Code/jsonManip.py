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
#print("Configuration actuelle : \n"+json.dumps(configuration, indent=2))


print("Configuration globale actuelle : \n"+json.dumps(configuration["globals"], indent=2))


if input("Ajouter un réseau ? o/n : ")=="o":
    nname=input("Nom du Routeur : ")
    nip=input("Range Ip : ")
    nmask=input("Masque reseau : ")
    newNetwork={
            "name": nname,
            "ip": nip,
            "mask": nmask
        }
    configuration["globals"]["networks"].append(newNetwork)
    with open("JSON/test.json", "w") as json_file: 
        json.dump(configuration,json_file,indent=4)

networks=[]
for network in configuration["globals"]["networks"] :
    networks.append(network["name"])

print("")
print("Configuration actuelle des routeurs: \n"+json.dumps(configuration["routers"], indent=2))
print("")
if input("Ajouter un routeur ? o/n : ")=="o":
    rname=input("Nom du Routeur : ")
    rnum=input("Numero du Routeur : ")
    ok="o"
    interfaces=[]
    while ok == "o" :
        print("ajout d'une interface : \n")
        if input("Loopback ? o/n ")=="o":
            interface={
                        "name": "loopback",
                    }
        else :
            iname=input("nom de l'interface : ")
            for i in range(len(networks)):
                    print(str(i)+"."+networks[i])
            net=input("A quel reseau appartient cette interface  ? (entrer le numero) : ")
            interface={
                            "name": iname,
                            "network": networks[int(net)],
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
