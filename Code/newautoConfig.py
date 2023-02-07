import json
import os
import sys
from jinja2 import Template

# Récupération des données
def get_data_from_json(name_json):
    # ouvrir le fichier JSON
    if os.path.exists(name_json):
        with open(name_json, "r") as json_file:
            data = json.load(json_file)
        return data
    else:
        print("le fichier newtest.json n'existe pas")

# Validation des données
def check_data(data):
    return True

# config bgp
def bgp(asnumber,neighbors):
    txt="router bgp "+asnumber+"\n"
    for neighbor in neighbors:
        txt+=" neighbor "+neighbor+"."+neighbor+"."+neighbor+"."+neighbor+" remote-as "+asnumber+"\n"
        txt+=" neighbor "+neighbor+"."+neighbor+"."+neighbor+"."+neighbor+" update-source Loopback0\n"
    txt+=" no auto-summary\n !\n address-family vpnv4\n"
    for neighbor in neighbors:
        txt+="  neighbor "+neighbor+"."+neighbor+"."+neighbor+"."+neighbor+" activate\n"
    txt+="!\n"
    return txt

def ospf(pid,loopback):
    txt="router ospf "+pid+"\n"
    txt+=" router-id "+loopback+"\n"
    txt+=" mpls ldp autoconfig\n"
    txt+="!\n"
    return txt

# config vrf
def vrf(name,routeDistinguisher,routeTarget):
    txt="vrf definition "+name+"\n"
    txt+=" rd "+routeDistinguisher+"\n"
    txt+=" route-target both "+routeTarget+"\n"
    txt+=" address-family ipv4\n"
    txt+=" exit-address-family\n"
    txt+="!\n"
    return txt

def vrfFamily(name,client,networks,number):
    txt="address-family ipv4 vrf "+name+"\n"
    for nets in networks:
        if nets["name"]==client:
            txt+=" neighbor "+nets["ip"]+number+" remote-as "+nets["bgpArea"]+"\n"
            txt+=" neighbor "+nets["ip"]+number+" activate\n"
    txt+="exit-address-family\n"
    txt+="!\n"
    return txt


networkIpsCounter={}
networks={}

# Récupération des données du JSON
configuration = get_data_from_json("JSON/newtest.json")
#print(json.dumps(configuration, indent=2))

# Vérification des données
if not check_data(configuration):
    sys.exit()

# Création des Template
with open("Template/template_router_basic.txt") as file:
    baseTemplate = Template(file.read())
with open("Template/template_router_interface.txt") as file:
    interfaceTemplate = Template(file.read())
with open("Template/template_router_interfaceOSPF.txt") as file:
    interfaceOSPFTemplate = Template(file.read())
with open("Template/template_router_vrfinterface.txt") as file:
    vrfinterfaceTemplate = Template(file.read())
with open("Template/template_router_end.txt") as file:
    endTemplate = Template(file.read())
with open("Template/template_router_vrfcreation.txt") as file:
    vrfcreationTemplate = Template(file.read())


# Rendu Template End
rendered_end = endTemplate.render()

#On créé un dictionnaire qui a pour clé chacun des liens et valeur le nombre de routeurs à qui on a donné un adresse dans le ss-réseau correspondant
ip_counter = {}
i =0
for router in configuration["routers"]:
    for link in router["links"]:
        ip_counter.setdefault(link[0],0)
        i+=1

print(ip_counter)        

ce_routers = {}



for router in configuration["routers"]:
    interface = 1
    
    rendered_base = baseTemplate.render(name=router["name"])
    configsRouter = []
    numRouter = router["name"][1:]
    classRouter = router["classe"]
    print(classRouter)
    loopback=numRouter+"."+numRouter+"."+numRouter+"."+numRouter
    
    #Generation de la loopback en fonction de CE ou PE/P (OSPF ou non)
    
    if classRouter == "CE":
        rendered_interface = interfaceTemplate.render(
            name="loopback 0",
            ip=loopback,
            mask="255.255.255.255"
        )
        configsRouter.append(rendered_interface)

        #Attribution des adresses IP pour chaque interface en fonction des liens et des attributions déjà faites
        
        for link in router["links"]:
            ip_counter[link[0]] +=1
            rendered_interface = interfaceTemplate.render(
                name=link[interface][1],
                ip="192.168."+str(link[0])+"."+str(ip_counter[link[0]]),
                mask="255.255.255.0"
            )
            configsRouter.append(rendered_interface)
            interface += 1

    #Pareil pour les PE/P

    else:
        rendered_interface = interfaceOSPFTemplate.render(
            name="loopback 0",
            ip=loopback,
            mask="255.255.255.255",
            PID = "42",
            area = "1"
        )
        configsRouter.append(rendered_interface)

        
        for link in router["links"]:
            ip_counter[link[0]] +=1
            rendered_interface = interfaceTemplate.render(
                name=link[interface][1],
                ip="192.168."+str(link[0])+"."+str(ip_counter[link[0]]),
                mask="255.255.255.0",
                PID = "42",
                area = "1"
            )
            configsRouter.append(rendered_interface)
            interface += 1

        if classRouter == "PE":
            listVPN =[]
            i=0
            for ce_router in configuration["routers"]:
                if ce_router["classe"] == "CE":
                    for link in router["links"]:
                        if link in ce_router["links"]:
                            print("PE Router {} is connected to CE Router {} with VPN {}".format(router["name"], ce_router["name"], ce_router["VPN"][i][1]))
                            vpnNumber = str(ce_router["VPN"][i][1])
                            if vpnNumber not in listVPN:
                                i+=1
                                listVPN.append(vpnNumber)
                                rendered_interface = vrfcreationTemplate.render(
                                    VPN = "VPN"+vpnNumber,
                                    routeDistinguisher = vpnNumber+":"+vpnNumber,
                                    routeTarget = vpnNumber+":"+vpnNumber
                                )
                                configsRouter.append(rendered_interface)

    
    


        
    
    # Génération des configurations pour chaque interface
    # for interface in router["interface"]:
    #     # if interface["name"] == "loopback" : 
    #     #     rendered_interface = interfaceTemplate.render(
    #     #         name="loopback 0",
    #     #         ip=router["numero"]+"."+router["numero"]+"."+router["numero"]+"."+router["numero"],
    #     #         mask=32
    #     #     )  


    #     if "vrfConfig" not in interface: #elif de base
    #         networkIpsCounter[interface["network"]]=+1

    #         if "ospfConfig" not in router:
    #             rendered_interface = interfaceTemplate.render(
    #                 name=interface["name"],
    #                 ip=networks[interface["network"]]["ip"]+str(networkIpsCounter[interface["network"]]),
    #                 mask=networks[interface["network"]]["mask"]
    #             )
    #         else:
    #             rendered_interface = interfaceOSPFTemplate.render(
    #                 name=interface["name"],
    #                 ip=networks[interface["network"]]["ip"]+str(networkIpsCounter[interface["network"]]),
    #                 mask=networks[interface["network"]]["mask"],
    #                 PID = router["ospfConfig"]["PID"],
    #                 area = router["ospfConfig"]["area"]
    #             )

    #     elif "vrfConfig" in interface:
    #         networkIpsCounter[interface["network"]]=+1
    #         rendered_interface = vrfinterfaceTemplate.render(
    #             VRFname=interface["vrfConfig"]["name"],
    #             name=interface["name"],
    #             ip=networks[interface["network"]]["ip"]+str(networkIpsCounter[interface["network"]]),
    #             mask=networks[interface["network"]]["mask"],
    #             PID = router["ospfConfig"]["PID"],
    #             area = router["ospfConfig"]["area"]
    #         )


    #     if "vrfConfig" in interface:
    #         print("vrfConfig exists "+interface["name"])
    #         configsRouter.append(vrf(interface["vrfConfig"]["name"],interface["vrfConfig"]["routeDistinguisher"],interface["vrfConfig"]["routeTarget"]))
    #         configsRouter.append(vrfFamily(interface["vrfConfig"]["name"],interface["network"],configuration["globals"]["networks"],str(networkIpsCounter[interface["network"]]+1)))
    #     else:
    #         print("vrfConfig doesn't exists "+router["name"])
    #     configsRouter.append(rendered_interface)

    # if "bgpConfig" in router:
    #     print("bgpConfig exists "+router["name"])
    #     configsRouter.append(bgp(router["bgpConfig"]["ASnumber"],router["bgpConfig"]["neighbors"]))
    # else:
    #     print("bgpConfig doesn't exists "+router["name"])

    # if "ospfConfig" in router:
    #     print("ospfConfig exists "+router["name"]+"\n")
    #     loopback=router["numero"]+"."+router["numero"]+"."+router["numero"]+"."+router["numero"]
    #     configsRouter.append(ospf(router["ospfConfig"]["PID"],loopback))
    # else:
    #     print("ospfConfig doesn't exists "+router["name"])

    # Ecriture des configurations pour chaque routeur
    
    print(ip_counter)
    with open("Configuration/i" + numRouter + "_startup-config.cfg", "w") as config_file:
        config_file.write(rendered_base)
        for config in configsRouter:
            config_file.write(config)
        config_file.write(rendered_end)






