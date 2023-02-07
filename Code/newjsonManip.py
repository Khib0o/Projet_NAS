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

#prends une liste d'entiers et retourne l'entier le plus haut auquel on ajoute 1
def determineNextlinkNumber(links):
    nextLink=1
    for link in links:
        if link>=nextLink:
            nextLink=link+1
    return nextLink

#prend en entrée la liste des routeurs et renvoit la liste des liens triés
def getAllLinks(routers):
    links=[]
    for router in routers:
        for link in router["links"]:
            if link not in links :
                links.append(link)
    links.sort()
    return links

#Saisie utilisateur de la classe du routeur
def choixClasseRouteur():
    print("1 : CE") 
    print("2 : PE") 
    print("3 : P") 
    rclass= input("Classe du Routeur : ")
    if rclass=="1":
        return "CE"
    if rclass=="2":
        return "PE"
    if rclass=="3":
        return "P"
    else:
        print("choix invalide, veuillez saisir un nombre entre 1 et 3 ")   
        return choixClasseRouteur()

#Saisie utilisateur du nom du routeur
def nomRouteur(routers):
    print("yo")
    rname=input("Nom du Routeur : ")
    for router in routers:
        if rname==router["name"]:
            print("Nom de routeur déjà existants : ")
            return nomRouteur(routers)
    return rname

#récupère l'existant
configuration = get_data_from_json("JSON/newtest.json")


print("Configuration actuelle des routeurs: \n"+json.dumps(configuration["routers"], indent=2))
print("-------------------")
print("0 : ne rien faire/quitter ")
print("1 : ajouter un routeur     | 2 supprimer un routeur")
print("3 : créer un nouveau lien  | 4 supprimer un lien")
print("5 : créer une VRF          | 6 supprimer une VRF\n")

choice = input("Que voulez vous faire ? : ")
print(choice)
while choice!="0":
    if choice=="1":#ajouter un routeur
        rname=nomRouteur(configuration["routers"])
        rclass=choixClasseRouteur()           
        newRouteur={
                "name": rname,
                "classe": rclass,
                "links":[]
            }
        if configuration["routers"]:
            while input("Creer une liaison ? o/n : ")=="o":
                print("routeurs existants")
                validAnswer=[]
                for i in range(len(configuration["routers"])):          
                    if (rclass=="P" and configuration["routers"][i]["classe"]!="CE")or(rclass=="CE" and configuration["routers"][i]["classe"]=="PE")or (rclass=="PE" and configuration["routers"][i]["classe"]!="PE"):
                        validAnswer.append(str(i))
                        print(str(i+1)+" : "+ configuration["routers"][i]["name"]+" classe : "+ configuration["routers"][i]["classe"])
                print("Entrer 0 pour annuler")
                rselected = input("Sélectionner le routeur auquel le lier ou annuler : ")
                if rselected!="0" and rselected in validAnswer:
                    links=getAllLinks(configuration["routers"])
                    for link in newRouteur["links"]:
                        links.append(link)
                    newLink=determineNextlinkNumber(links)
                    configuration["routers"][int(rselected)-1]["links"].append(newLink)
                    newRouteur["links"].append(newLink)
            if rclass == "PE":
                while input("Configurer une VRF ? o/n : ")=="o":
                    for l in range(len(newRouteur["links"])):
                        print(str(l+1)+" : lien "+str(newRouteur["links"][l]))
                    print("Entrer 0 pour annuler")
                    lselected = int(input("Sélectionner le routeur auquel le lier ou annuler : "))
                    if lselected!=0 and lselected in range(len(newRouteur["links"])+1):
                        VPNid = int(input("Entrer l'id du VPN à associer à ce lien : "))
                        if "VPNs" in newRouteur:
                            newRouteur["VPNs"].append([newRouteur["links"][lselected-1],VPNid])
                        else :
                            newRouteur["VPNs"]=[[newRouteur["links"][lselected-1],VPNid]]
        else :
            print("first router initialized")
        configuration["routers"].append(newRouteur)

    if choice=="2":#supprimer un routeur
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

    if choice=="3":#creer un nouveau lien
        for i in range(len(configuration["routers"])):
            print(str(i+1)+" : "+ configuration["routers"][i]["name"])
        print("Entrer 0 pour annuler")
        r1selected = input("Sélectionner le 1er routeur à lier ou annuler : ")
        r1selected = int(r1selected)-1
        validAnswer=[]
        rclass=configuration["routers"][r1selected]["classe"]
        for i in range(len(configuration["routers"])):          
            if (rclass=="P" and configuration["routers"][i]["classe"]!="CE")or(rclass=="CE" and configuration["routers"][i]["classe"]=="PE")or (rclass=="PE" and configuration["routers"][i]["classe"]!="PE"):
                validAnswer.append(i)
                print(str(i+1)+" : "+ configuration["routers"][i]["name"]+" classe : "+ configuration["routers"][i]["classe"])
        print("Entrer 0 pour annuler")
        r2selected = int(input("Sélectionner le 2nd routeur à lier ou annuler : "))-1
        if r1selected!=-1 and r1selected!=r2selected and r2selected in validAnswer:
            newLink=determineNextlinkNumber(getAllLinks(configuration["routers"]))
            configuration["routers"][r1selected]["links"].append(newLink)
            configuration["routers"][r2selected]["links"].append(newLink)

    if choice=="4":#supprimer un lien
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
        validAnswer=[]
        for i in range(len(configuration["routers"])):
            if configuration["routers"][i]["classe"]=="PE":
                validAnswer.append(i)
                print(str(i+1)+" : "+ configuration["routers"][i]["name"])
        print("Entrer 0 pour annuler")
        rselected = int(input("Sélectionner le routeur sur lequel mettre une VRF ou annuler : "))-1
        if rselected!=-1 and rselected in validAnswer:
            for l in range(len(configuration["routers"][rselected]["links"])):
                print(str(l+1)+" : lien "+str(configuration["routers"][rselected]["links"][l]))
            print("Entrer 0 pour annuler")
            lselected = int(input("Sélectionner le lien sur lequel configurer une VRF ou annuler : "))
            if lselected!=0:
                VPNid = int(input("Entrer l'id du VPN à associer à ce lien : "))
                if "VPNs" in configuration["routers"][rselected]:
                    configuration["routers"][rselected]["VPNs"].append([configuration["routers"][rselected]["links"][lselected-1],VPNid])
                else :
                    configuration["routers"][rselected]["VPNs"]=[[configuration["routers"][rselected]["links"][lselected-1],VPNid]]
   
    if choice=="6":#supprimer une VRF
        for i in range(len(configuration["routers"])):
            if "VPNs" in configuration["routers"][i]:
                print(str(i+1)+" : "+ configuration["routers"][i]["name"])
        print("Entrer 0 pour annuler")
        rselected = input("Sélectionner le routeur sur lequel se trouve la vrf à supprimer ou annuler : ")
        if rselected!="0":
            for ivpn in range(len(configuration["routers"][int(rselected)-1]["VPNs"])):
                print(str(ivpn+1)+" : "+str(configuration["routers"][int(rselected)-1]["VPNs"][ivpn]))
            print("Entrer 0 pour annuler")
            vpnselected=int(input("Sélectionner la vrf à supprimer ou annuler : "))
            if vpnselected!=0:
                del(configuration["routers"][int(rselected)-1]["VPNs"][vpnselected-1])
                if configuration["routers"][int(rselected)-1]["VPNs"]==[]:
                    del configuration["routers"][int(rselected)-1]["VPNs"]

    if choice=="7":#voir la config actuelle des routeurs
        print("Configuration actuelle des routeurs: \n"+json.dumps(configuration["routers"], indent=2))


    with open("JSON/newtest.json", "w") as json_file: 
        json.dump(configuration,json_file,indent=4)
    print("-------------------")
    print("0 : ne rien faire")
    print("1 : ajouter un routeur     | 2 supprimer un routeur")
    print("3 : créer un nouveau lien  | 4 supprimer un lien")
    print("5 : créer une VRF          | 6 supprimer une VRF")
    print("7 : Afficher la config actuelle \n")
    choice = input("Que voulez vous faire ? : ")