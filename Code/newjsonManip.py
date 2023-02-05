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

def determineNextlinkNumber(links):
    nextLink=1
    for link in links:
        if link>=nextLink:
            nextLink=link+1
    return nextLink

def getAllLinks(routers):
    links=[]
    for router in routers:
        for link in router["links"]:
            if link not in links :
                links.append(link)
    links.sort()
    return links

configuration = get_data_from_json("JSON/newtest.json")
#print("Configuration actuelle : \n"+json.dumps(configuration, indent=2))


print("Configuration actuelle des routeurs: \n"+json.dumps(configuration["routers"], indent=2))

print("-------------------")
print("0 : ne rien faire")
print("1 : ajouter un routeur     | 2 supprimer un routeur")
print("3 : créer un nouveau lien  | 4 supprimer un lien")
print("5 : créer une VRF          | 6 supprimer une VRF (pas encore fait)\n")
choice = input("Que voulez vous faire ? : ")
while choice!="0":
    if choice=="1":
        rname=input("Nom du Routeur : ")
        rclass=input("Classe du Routeur (CE/P/PE): ")
        newRouteur={
                "name": rname,
                "classe": rclass,
                "links":[]
            }
        if configuration["routers"]:
            while input("Creer une liaison ? o/n : ")=="o":
                print("routeurs existants")
                for i in range(len(configuration["routers"])):
                    print(str(i+1)+" : "+ configuration["routers"][i]["name"])
                print("Entrer 0 pour annuler")
                rselected = input("Sélectionner le routeur auquel le lier ou annuler : ")
                if rselected!="0":
                    links=getAllLinks(configuration["routers"])
                    for link in newRouteur["links"]:
                        links.append(link)
                    print("links :")
                    print(links)
                    newLink=determineNextlinkNumber(links)
                    print("nextLink")
                    print(newLink)
                    configuration["routers"][int(rselected)-1]["links"].append(newLink)
                    newRouteur["links"].append(newLink)
            while input("Configurer un VPN ? o/n : ")=="o":
                for l in range(len(newRouteur["links"])):
                    print(str(l)+" : lien "+str(newRouteur["links"][l]))
                print("Entrer 0 pour annuler")
                lselected = input("Sélectionner le routeur auquel le lier ou annuler : ")
                if lselected!="0":
                    VPNid = int(input("Entrer l'id du VPN à associer à ce lien : "))
                    if "VPNs" in newRouteur:
                        newRouteur["VPNs"].append([newRouteur["links"][l],VPNid])
                    else :
                        newRouteur["VPNs"]=[[newRouteur["links"][l],VPNid]]
        else :
            print("first router initialized")
        configuration["routers"].append(newRouteur)

    if choice=="2":
        for i in range(len(configuration["routers"])):
            print(str(i+1)+" : "+ configuration["routers"][i]["name"])
        print("Entrer 0 pour annuler")
        rselected = input("Sélectionner le routeur à supprimer ou annuler : ")
        if rselected!="0":
            for link in configuration["routers"][int(rselected)-1]["links"]:
                for i in range(len(configuration["routers"])):
                    if i!=int(rselected)-1:
                        for j in range(len(configuration["routers"][i]["links"])):
                            if link==configuration["routers"][i]["links"][j]:
                                del(configuration["routers"][i]["links"][j])
            del configuration["routers"][int(rselected)-1]

    if choice=="3":
        for i in range(len(configuration["routers"])):
            print(str(i+1)+" : "+ configuration["routers"][i]["name"])
        print("Entrer 0 pour annuler")
        r1selected = input("Sélectionner le 1er routeur à lier ou annuler : ")
        r2selected = input("Sélectionner le 2nd routeur à lier ou annuler : ")
        if r1selected!="0" and r2selected!="0" and r1selected!=r2selected:
            newLink=determineNextlinkNumber(getAllLinks(configuration["routers"]))
            configuration["routers"][int(r1selected)-1]["links"].append(newLink)
            configuration["routers"][int(r2selected)-1]["links"].append(newLink)

    if choice=="4":
        links=getAllLinks(configuration["routers"])
        for link in links:
            print(str(link)+" : lien "+str(link))
        print("Entrer 0 pour annuler")
        linkSelected = input("Sélectionner le lien à supprimer ou annuler : ")

        if linkSelected!="0":
            for i in range(len(configuration["routers"])):
                for j in range(len(configuration["routers"][i]["links"])):
                    if int(linkSelected)==configuration["routers"][i]["links"][j]:
                        del(configuration["routers"][i]["links"][j])

    if choice=="5":#creer une VRF
        for i in range(len(configuration["routers"])):
            print(str(i+1)+" : "+ configuration["routers"][i]["name"])
        print("Entrer 0 pour annuler")
        rselected = input("Sélectionner le routeur sur lequel mettre une VRF ou annuler : ")
        if rselected!="0":
            for l in range(len(configuration["routers"][int(rselected)-1]["links"])):
                print(str(l)+" : lien "+str(configuration["routers"][int(rselected)-1]["links"][l]))
            print("Entrer 0 pour annuler")
            lselected = input("Sélectionner le routeur auquel le lier ou annuler : ")
            if lselected!="0":
                VPNid = int(input("Entrer l'id du VPN à associer à ce lien : "))
                if "VPNs" in configuration["routers"][int(rselected)-1]:
                    configuration["routers"][int(rselected)-1]["VPNs"].append([configuration["routers"][int(rselected)-1]["links"][l],VPNid])
                else :
                    configuration["routers"][int(rselected)-1]["VPNs"]=[[configuration["routers"][int(rselected)-1]["links"][l],VPNid]]

    with open("JSON/newtest.json", "w") as json_file: 
        json.dump(configuration,json_file,indent=4)
    print("-------------------")
    print("0 : ne rien faire")
    print("1 : ajouter un routeur     | 2 supprimer un routeur")
    print("3 : créer un nouveau lien  | 4 supprimer un lien")
    print("5 : créer une VRF          | 6 supprimer une VRF (pas encore fait)\n")
    choice = input("Que voulez vous faire ? : ")