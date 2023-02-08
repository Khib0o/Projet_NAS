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
        print("le fichier conf.json n'existe pas")

oui=["o","oui","O","OUI","Oui","OUi","oUI","ouI","y","yes","Y","YES","Yes","YEs"]
validInterfaces=["g1/0","g2/0","g3/0"]
def afficheJson(routers):
    for router in routers:
        if "VPN" in router:
            print("Name : "+router["name"]+" ; Classe : "+router["classe"]+" ; Links : "+str(router["links"])+" ; VPN : "+str(router["VPN"]))
        elif "AS_BGP" in  router:
            print("Name : "+router["name"]+" ; Classe : "+router["classe"]+" ; Links : "+str(router["links"])+" ; AS_BGP : "+str(router["AS_BGP"]))
        else:
            print("Name : "+router["name"]+" ; Classe : "+router["classe"]+" ; Links : "+str(router["links"]))


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
    rname=input("Nom du Routeur : ")
    for router in routers:
        if rname==router["name"]:
            print("Nom de routeur déjà existant : ")
            return nomRouteur(routers)
    return rname

#récupère l'existant
configuration = get_data_from_json("conf.json")


print("Configuration actuelle des routeurs: \n")
afficheJson(configuration["routers"])
print("-------------------")
print("0 : Ne rien faire/quitter ")
print("1 : Ajouter un routeur         | 2 : Supprimer un routeur")
print("3 : Créer un nouveau lien      | 4 : Supprimer un lien")
print("5 : Créer un VPN               | 6 : Supprimer une VPN")
print("7 : Ajouter un numero d'AS     | 8 : Supprimer un numero d'AS")
print("9 : Afficher la config actuelle ")
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
            validChoice =True
            if input("Creer une liaison ? o/n : ") in oui:
                while True:
                    interface=input("Sur quelle interface creer la liaison ? ")
                    if interface in validInterfaces:
                        break
                    else:
                        print("interface incorrecte, doit être g1/0,g2/0 ou g3/0")
                print("routeurs existants")
                validAnswer=[]
                for i in range(len(configuration["routers"])):          
                    print(str(i+1)+" : "+ configuration["routers"][i]["name"]+" classe : "+ configuration["routers"][i]["classe"])
                print("Entrer 0 pour annuler")
                rselected = int(input("Sélectionner le routeur auquel le lier ou annuler : "))-1
                if rselected>-1:
                    if configuration["routers"][rselected]["classe"]=="CE" and rclass=="P":
                        print("WARNING : vous essayez de lier votre routeur (P) a un CE.")
                        if input("Changer la classe de votre routeur pour PE ? ") in oui:
                            newRouteur["classe"]="PE"
                        else:
                            validChoice=False
                    elif configuration["routers"][rselected]["classe"]=="P" and rclass=="CE":
                        print("WARNING : vous essayez de lier votre routeur (CE) a un P.")
                        if input("Changer la classe du second routeur pour PE ? ") in oui:
                            configuration["routers"][rselected]["classe"]="PE"
                        else:
                            validChoice=False
                    elif configuration["routers"][rselected]["classe"]=="CE" and rclass=="CE":
                        print("WARNING : vous essayez de lier votre routeur (CE) a un CE.")
                        if input("Changer la classe du second routeur pour PE ? ") in oui:
                            configuration["routers"][rselected]["classe"]="PE"
                            print("good rep")
                        else:
                            print("fausse rep")
                            validChoice=False

                    if(validChoice):
                        links=getAllLinks(configuration["routers"])
                        for link in newRouteur["links"]:
                            links.append(link)
                        newLink=determineNextlinkNumber(links)
                        while True:
                            rselectedInterface=input("Sur quelle interface du routeur creer la liaison ? ")
                            if rselectedInterface in validInterfaces:
                                break
                            else:
                                print("interface incorrecte, doit être g1/0,g2/0 ou g3/0")
                                
                        configuration["routers"][rselected]["links"].append([newLink,rselectedInterface])
                        newRouteur["links"].append([newLink,interface])
                    else:
                        del newRouteur

            if rclass == "CE" and validChoice:
                if input("Configurer une VRF ? o/n : ") in oui:
                    for l in range(len(newRouteur["links"])):
                        print(str(l+1)+" : lien "+str(newRouteur["links"][l]))
                    print("Entrer 0 pour annuler")
                    lselected = int(input("Sélectionner le lien auquel la lier ou annuler : "))
                    if lselected!=0 and lselected in range(len(newRouteur["links"])+1):
                        VPNid = int(input("Entrer l'id du VPN à associer à ce lien : "))
                        if "VPN" in newRouteur:
                            configuration["routers"][rselected]["VPN"].append([VPNid,newRouteur["links"][lselected-1][1]])
                        else :
                           configuration["routers"][rselected]["VPN"]=[[VPNid,newRouteur["links"][lselected-1][1]]]
            else :
                print("first router initialized")
            if(validChoice):
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
                            #print(str(configuration["routers"][i]["links"][j][0])+"||"+str(link[0]))
                            if link[0]==configuration["routers"][i]["links"][j][0]:
                                print("on delete")
                                del(configuration["routers"][i]["links"][j])
                                break
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
                if configuration["routers"][r1selected]["classe"]=="CE" and configuration["routers"][r2selected]["classe"]=="P":
                    print("WARNING : vous essayer de lier votre routeur P a un CE.")
                    if input("Changer la classe du premier routeur pour PE ? ") in oui:
                        newRouteur["classe"]="PE"
                elif configuration["routers"][r1selected]["classe"]=="P" and configuration["routers"][r2selected]["classe"]=="CE":
                    print("WARNING : vous essayer de lier un routeur CE a un P.")
                    if input("Changer la classe du second routeur pour PE ? ") in oui:
                        configuration["routers"][r1selected]["classe"]="PE"
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
            if configuration["routers"][i]["classe"]=="PE":
                validAnswer.append(i)
                print(str(i+1)+" : "+ configuration["routers"][i]["name"])
        print("Entrer 0 pour annuler")
        rselected = int(input("Sélectionner le routeur sur lequel mettre une VRF ou annuler : "))-1
        if rselected>-1 and rselected in validAnswer:
            for l in range(len(configuration["routers"][rselected]["links"])):
                print(str(l+1)+" : lien "+str(configuration["routers"][rselected]["links"][l][1]))
            print("Entrer 0 pour annuler")
            lselected = int(input("Sélectionner l'interface sur laquelle configurer une VRF ou annuler : "))
            if lselected!=0:
                VPNid = int(input("Entrer l'id du VPN à associer à ce lien : "))
                if "VPN" in configuration["routers"][rselected]:
                    configuration["routers"][rselected]["VPN"].append([VPNid,configuration["routers"][rselected]["links"][lselected-1][1]])
                else :
                    configuration["routers"][rselected]["VPN"]=[VPNid,configuration["routers"][rselected]["links"][lselected-1][1]]
   
    if choice=="6":#supprimer une VRF
        for i in range(len(configuration["routers"])):
            if "VPN" in configuration["routers"][i]:
                print(str(i+1)+" : "+ configuration["routers"][i]["name"])
        print("Entrer 0 pour annuler")
        rselected = input("Sélectionner le routeur sur lequel se trouve la vrf à supprimer ou annuler : ")
        if rselected!="0":
            for ivpn in range(len(configuration["routers"][int(rselected)-1]["VPN"])):
                print(str(ivpn+1)+" : "+str(configuration["routers"][int(rselected)-1]["VPN"][ivpn]))
            print("Entrer 0 pour annuler")
            vpnselected=int(input("Sélectionner la vrf à supprimer ou annuler : "))
            if vpnselected!=0:
                del(configuration["routers"][int(rselected)-1]["VPN"][vpnselected-1])
                if configuration["routers"][int(rselected)-1]["VPN"]==[]:
                    del configuration["routers"][int(rselected)-1]["VPN"]


    if choice=="7":#nouvelle session BGP
        validAnswer=[]
        freeSpace = False
        for i in range(len(configuration["routers"])):
            if configuration["routers"][i]["classe"]=="CE" and "AS_BGP" not in configuration["routers"][i]:
                validAnswer.append(i)
                print(str(i+1)+" : "+ configuration["routers"][i]["name"])
                freeSpace = True
            
        if(freeSpace):
            print("Entrer 0 pour annuler")
            rselected = int(input("Sélectionner le routeur sur lequel mettre une VRF ou annuler : "))-1

            if rselected>-1 and rselected in validAnswer:
                configuration["routers"][rselected]["AS_BGP"]=int(input("Entrer le numero d'AS de la session BGP "))
        else:
            print("Il n'y a aucun CE sans session BGP\n")
            
    
    if choice=="8":#supprimer une session BGP
        for i in range(len(configuration["routers"])):
            if "AS_BGP" in configuration["routers"][i]:
                print(str(i+1)+" : "+ configuration["routers"][i]["name"])
        print("Entrer 0 pour annuler")
        rselected = input("Sélectionner le routeur sur lequel se trouve la vrf à supprimer ou annuler : ")
        if rselected!="0":
            del configuration["routers"][int(rselected)-1]["AS_BGP"]

    if choice=="9":#voir la config actuelle des routeurs
        print("Configuration actuelle des routeurs: \n")
        afficheJson(configuration["routers"])

    if choice=="10":
        exec(open("autoconfig.py").read())
        print("configs generees")

    with open("conf.json", "w") as json_file: 
        json.dump(configuration,json_file,indent=4)
    print("-------------------")
    print("Configuration actuelle des routeurs: \n")
    afficheJson(configuration["routers"])
    print("0 : Quitter")
    print("1 : ajouter un routeur     | 2 supprimer un routeur")
    print("3 : créer un nouveau lien  | 4 supprimer un lien")
    print("5 : créer une VRF          | 6 supprimer une VRF")
    print("7 : nouvelle session BGP   | 8 supprimer une session BGP")
    print("9 : Afficher la config actuelle ")
    print("10 : generer les fichiers configs des routeurs\n")
    choice = input("Que voulez vous faire ? : ")