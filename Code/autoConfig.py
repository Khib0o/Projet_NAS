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

def ipconfig(name,ip,mask,ospfNum,ospfArea):
    txt="interface "+name+"\n"
    txt+="ip address "+ip+" "+mask+"\n"
    if ospfNum!=-1:
        txt+="ip ospf "+ospfNum+" area "+ospfArea+"\n"
    txt+="no shutdown\n"
    txt+="!\n"
    return txt

def ospfConfig(ospfNum,rId):
    txt="router ospf "+ospfNum+"\n"
    txt+="router-id "+rId+"."+rId+"."+rId+"."+rId+"\n"
    txt+="mpls ldp autoconfig\n"
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
    configsRouter = ""
    # Génération des configurations pour chaque interface
    for interface in router["interface"]:
        if interface["name"] == "loopback" : 
            name="loopback 0"
            ip=router["numero"]+"."+router["numero"]+"."+router["numero"]+"."+router["numero"]
            mask=32
            ospfNum=-1
            ospfArea=-1
            if "ospf" in interface:
                ospfNum=router["ospf"]["ospfNum"]
                ospfArea=interface["ospf"]["ospfArea"]     
        else :
            networkIpsCounter[interface["network"]]=+1
            name=interface["name"]
            ip=networks[interface["network"]]["ip"]+str(networkIpsCounter[interface["network"]])
            mask=networks[interface["network"]]["mask"]
            ospfNum=-1
            ospfArea=-1
            if "ospf" in interface:
                ospfNum = router["ospf"]["ospfNum"]
                ospfArea = interface["ospf"]["ospfArea"]
        print(name)
        print(ip)
        print(mask)
        print(ospfNum)
        print(ospfArea)
        configsRouter+=ipconfig(str(name),str(ip),str(mask),str(ospfNum),str(ospfArea))
    if "ospf" in router:
        configsRouter+=ospfConfig(router["ospf"]["ospfNum"],router["numero"])
    if "bgpConfig" in router:
        print("bgpConfig exists "+router["name"])
        configsRouter+=bgp(router["bgpConfig"]["ASnumber"],router["bgpConfig"]["neighbors"])
    else:
        print("bgpConfig doesn't exists "+router["name"])

    # Ecriture des configurations pour chaque routeur
    with open("Configuration/i" + router["numero"] + "_startup-config.cfg", "w") as config_file:
        config_file.write(rendered_base)
        for config in configsRouter:
            config_file.write(config)
        config_file.write(rendered_end)






