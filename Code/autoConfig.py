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
        print("le fichier test.json n'existe pas")

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


# config vrf
def vrf(name,routeTarget):
    txt="vrf definition "+name+"\n"
    txt+=" rd "+routeTarget+":"+routeTarget+"\n"
    txt+=" route-target both "+routeTarget+":"+routeTarget+"\n"
    txt+=" address-family ipv4\n"
    txt+=" exit-address-family\n"
    txt+="!\n"
    return txt


networkIpsCounter={}
networks={}

# Récupération des données du JSON
configuration = get_data_from_json("JSON/test.json")
#print(json.dumps(configuration, indent=2))

# Vérification des données
if not check_data(configuration):
    sys.exit()

# Création des Template
with open("Template/template_router_basic.txt") as file:
    baseTemplate = Template(file.read())
with open("Template/template_router_interface.txt") as file:
    interfaceTemplate = Template(file.read())
with open("Template/template_router_end.txt") as file:
    endTemplate = Template(file.read())

# Rendu Template End
rendered_end = endTemplate.render()


for network in configuration["globals"]["networks"]:#prépare à compter les ips déja paramétrées
    networkIpsCounter[network["name"]]=0
    networks[network["name"]]=network

print(networks)

# Rendu Template Basic et Interface pour chaque router
for router in configuration["routers"]:
    rendered_base = baseTemplate.render(name=router["name"])
    configsRouter = []
    # Génération des configurations pour chaque interface
    for interface in router["interface"]:
        if interface["name"] == "loopback" : 
            rendered_interface = interfaceTemplate.render(
                name="loopback 0",
                ip=router["numero"]+"."+router["numero"]+"."+router["numero"]+"."+router["numero"],
                mask=32
            )  
        else :
            networkIpsCounter[interface["network"]]=+1
            rendered_interface = interfaceTemplate.render(
                name=interface["name"],
                ip=networks[interface["network"]]["ip"]+str(networkIpsCounter[interface["network"]]),
                mask=networks[interface["network"]]["mask"]
            )
        configsRouter.append(rendered_interface)

    if "bgpConfig" in router:
        print("bgpConfig exists "+router["name"])
        configsRouter.append(bgp(router["bgpConfig"]["ASnumber"],router["bgpConfig"]["neighbors"]))
    else:
        print("bgpConfig doesn't exists "+router["name"])

    if "vrfConfig" in router:
        print("vrfConfig exists "+router["name"])
        configsRouter.append(vrf(router["vrfConfig"]["name"],router["vrfConfig"]["routeTarget"]))
    else:
        print("vrfConfig doesn't exists "+router["name"])

    # Ecriture des configurations pour chaque routeur
    with open("Configuration/i" + router["numero"] + "_startup-config.cfg", "w") as config_file:
        config_file.write(rendered_base)
        for config in configsRouter:
            config_file.write(config)
        config_file.write(rendered_end)






