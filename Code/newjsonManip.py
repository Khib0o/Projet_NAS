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

oui=["o","oui","O","OUI","Oui","OUi","oUI","ouI","y","yes","Y","YES","Yes","YEs"]
def afficheJson(routers):
    for router in routers:
        if "VPNs" in router:
            print("name : "+router["name"]+" ; Classe : "+router["classe"]+" ; Links : "+str(router["links"])+" ; VPNs : "+str(router["VPNs"]))
        else:
            print("name : "+router["name"]+" ; Classe : "+router["classe"]+" ; Links : "+str(router["links"]))

#prends une liste d'entiers et retourne l'entier le plus haut auquel on ajoute 1
def determineNextlinkNumber(links):
    nextLink=1
    for link in links:
        if link[0]>=nextLink:
            nextLink=link[0]+1
    return nextLink

#prend en entrée la liste des routeurs et renvoit la liste des liens triés
def getAllLinks(routers):
    links=[]
    for router in routers:
        for link in router["links"]:
            if link[0] not in links :
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


print("Configuration actuelle des routeurs: \n")
afficheJson(configuration["routers"])
print("-------------------")
print("0 : ne rien faire/quitter ")
print("1 : ajouter un routeur     | 2 supprimer un routeur")
print("3 : créer un nouveau lien  | 4 supprimer un lien")
print("5 : créer une VRF          | 6 supprimer une VRF")
print("7 : nouvelle session BGP     | 8 supprimer une session BGP")
print("9 : Afficher la config actuelle ")
print("10 : generer les fichiers configs des routeurs\n")
choice = input("Que voulez vous faire ? : ")
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
            while input("Creer une liaison ? o/n : ") in oui:
                interface=input("Sur quelle interface creer la liaison ? ")
                print("routeurs existants")
                validAnswer=[]
                for i in range(len(configuration["routers"])):          
                    print(str(i+1)+" : "+ configuration["routers"][i]["name"]+" classe : "+ configuration["routers"][i]["classe"])
                print("Entrer 0 pour annuler")
                rselected = int(input("Sélectionner le routeur auquel le lier ou annuler : "))-1
                if rselected>-1:
                    if configuration["routers"][rselected]["classe"]=="CE" and rclass=="P":
                        print("WARNING : vous essayer de lier votre routeur (P) a un CE.")
                        if input("Changer la classe de votre routeur pour PE ? ") in oui:
                            newRouteur["classe"]="PE"
                    elif configuration["routers"][rselected]["classe"]=="P" and rclass=="CE":
                        print("WARNING : vous essayer de lier votre routeur (CE) a un P.")
                        if input("Changer la classe du second routeur pour PE ? ") in oui:
                            configuration["routers"][rselected]["classe"]="PE"
                    links=getAllLinks(configuration["routers"])
                    for link in newRouteur["links"]:
                        links.append(link)
                    newLink=determineNextlinkNumber(links)
                    rselectedInterface=input("Sur quelle interface creer la liaison ? ")
                    configuration["routers"][rselected]["links"].append([newLink,rselectedInterface])
                    newRouteur["links"].append([newLink,interface])
            if rclass == "CE":
                while input("Configurer une VRF ? o/n : ") in oui:
                    for l in range(len(newRouteur["links"])):
                        print(str(l+1)+" : lien "+str(newRouteur["links"][l]))
                    print("Entrer 0 pour annuler")
                    lselected = int(input("Sélectionner le routeur auquel le lier ou annuler : "))
                    if lselected!=0 and lselected in range(len(newRouteur["links"])+1):
                        VPNid = int(input("Entrer l'id du VPN à associer à ce lien : "))
                        rts=[]
                        rts.append(int(input("entrez la route target : ")))
                        while input("configurer une autre route target o/n ? ") in oui:
                            print("pour anuler entrez 0")
                            newrt=int(input("entrez la route target : "))
                            if newrt!=0:
                                rts.append(newrt)
                        if "VPNs" in newRouteur:
                            newRouteur["VPNs"].append([VPNid,newRouteur["links"][lselected-1][0]]+rts)
                        else :
                            newRouteur["VPNs"]=[[VPNid,newRouteur["links"][lselected-1][0]]+rts]
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
        r1Interface = input("Entrer le nom de l'interface sur laquelle sera faite le lien : ")
        if r1selected>-1:
            validAnswer=[]
            rclass=configuration["routers"][r1selected]["classe"]
            for i in range(len(configuration["routers"])):
                    print(str(i+1)+" : "+ configuration["routers"][i]["name"]+" classe : "+ configuration["routers"][i]["classe"])
            print("Entrer 0 pour annuler")
            r2selected = int(input("Sélectionner le 2nd routeur à lier ou annuler : "))-1
            if r2selected>-1 and r1selected!=r2selected :
                if configuration["routers"][rselected]["classe"]=="CE" and configuration["routers"][r2selected]["classe"]=="P":
                    print("WARNING : vous essayer de lier votre routeur P a un CE.")
                    if input("Changer la classe du premier routeur pour PE ? ") in oui:
                        newRouteur["classe"]="PE"
                elif configuration["routers"][rselected]["classe"]=="P" and configuration["routers"][r2selected]["classe"]=="CE":
                    print("WARNING : vous essayer de lier un routeur CE a un P.")
                    if input("Changer la classe du second routeur pour PE ? ") in oui:
                        configuration["routers"][rselected]["classe"]="PE"
                r2Interface = input("Entrer le nom de l'interface sur laquelle sera faite le lien sur le second routeur: ")
                newLink=determineNextlinkNumber(getAllLinks(configuration["routers"]))
                configuration["routers"][r1selected]["links"].append([newLink,r1Interface])
                configuration["routers"][r2selected]["links"].append([newLink,r2Interface])

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
            if configuration["routers"][i]["classe"]=="CE":
                validAnswer.append(i)
                print(str(i+1)+" : "+ configuration["routers"][i]["name"])
        print("Entrer 0 pour annuler")
        rselected = int(input("Sélectionner le routeur sur lequel mettre une VRF ou annuler : "))-1
        if rselected>-1 and rselected in validAnswer:
            for l in range(len(configuration["routers"][rselected]["links"])):
                print(str(l+1)+" : lien "+str(configuration["routers"][rselected]["links"][l][0]))
            print("Entrer 0 pour annuler")
            lselected = int(input("Sélectionner le lien sur lequel configurer une VRF ou annuler : "))
            if lselected!=0:
                VPNid = int(input("Entrer l'id du VPN à associer à ce lien : "))
                rts=[]
                rts.append(int(input("entrez la route target : ")))
                while input("configurer une autre route target o/n ? ") in oui:
                    print("pour anuler entrez 0")
                    newrt=int(input("entrez la route target : "))
                    if newrt!=0:
                        rts.append(newrt)
                if "VPNs" in configuration["routers"][rselected]:
                    configuration["routers"][rselected]["VPNs"].append([VPNid,configuration["routers"][rselected]["links"][lselected-1][0]]+rts)
                else :
                    configuration["routers"][rselected]["VPNs"]=[VPNid,configuration["routers"][rselected]["links"][lselected-1][0]]+rts
   
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


    if choice=="7":#nouvelle session BGP
        validAnswer=[]
        for i in range(len(configuration["routers"])):
            if configuration["routers"][i]["classe"]=="CE" and "BGP" not in configuration["routers"][i]:
                validAnswer.append(i)

                print(str(i+1)+" : "+ configuration["routers"][i]["name"])
        print("Entrer 0 pour annuler")
        rselected = int(input("Sélectionner le routeur sur lequel mettre une VRF ou annuler : "))-1

        if rselected>-1 and rselected in validAnswer:
            configuration["routers"][rselected]["BGP"]=int(input("Entrer le numero d'AS de la session BGP "))
            
    
    if choice=="8":#supprimer une session BGP
        for i in range(len(configuration["routers"])):
            if "BGP" in configuration["routers"][i]:
                print(str(i+1)+" : "+ configuration["routers"][i]["name"])
        print("Entrer 0 pour annuler")
        rselected = input("Sélectionner le routeur sur lequel se trouve la vrf à supprimer ou annuler : ")
        if rselected!="0":
            del configuration["routers"][int(rselected)-1]["BGP"]

    if choice=="9":#voir la config actuelle des routeurs
        print("Configuration actuelle des routeurs: \n")
        afficheJson(configuration["routers"])

    if choice=="10":
        exec(open("programmeTest.py").read())
        print("configs generees")

    with open("JSON/newtest.json", "w") as json_file: 
        json.dump(configuration,json_file,indent=4)
    print("-------------------")
    print("0 : Quitter")
    print("1 : ajouter un routeur     | 2 supprimer un routeur")
    print("3 : créer un nouveau lien  | 4 supprimer un lien")
    print("5 : créer une VRF          | 6 supprimer une VRF")
    print("7 : nouvelle session BGP   | 8 supprimer une session BGP")
    print("9 : Afficher la config actuelle ")
    print("10 : generer les fichiers configs des routeurs\n")
    choice = input("Que voulez vous faire ? : ")