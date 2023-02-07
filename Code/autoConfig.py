import json
import os
import sys
from jinja2 import Template

# Constante globale
mask_loopback = "255.255.255.255"
mask_ip = "255.255.255.0"
ip_loopback = "192.168.255."
ip_réseau = "192.168."

def extract_string(s):
    start =     s.find("_") + len("_")
    end = s.find("_", start)
    return s[start:end]

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
def bgp(asnumber, neighbors):
    txt="\nrouter bgp " + asnumber + "\n"
    for neighbor in neighbors:
        txt+=" neighbor "+neighbor+"."+neighbor+"."+neighbor+"."+neighbor+" remote-as "+asnumber+"\n"
        txt+=" neighbor "+neighbor+"."+neighbor+"."+neighbor+"."+neighbor+" update-source Loopback0\n"
    txt+=" no auto-summary\n ! \n address-family vpnv4\n"
    for neighbor in neighbors:
        txt+="  neighbor "+neighbor+"."+neighbor+"."+neighbor+"."+neighbor+" activate\n"
    txt+="!\n"
    return txt

# config vrf
def create_vrf(name, as_number, route_d, vrf_config):
    txt="!\n!--- " + name + " commands.\n!\n"
    txt+="vrf definition " + name + "\n"
    txt+=" rd " + as_number + ":" + route_d + "\n"
    txt+=" route-target import " + as_number + ":" + vrf_config[name]["RT"] + "\n"
    txt+=" route-target export " + as_number + ":" + vrf_config[name]["RT"] + "\n"
    for color in vrf_config[name]["RT_import"]:
        txt+=" route-target export " + as_number + ":" + vrf_config[color]["RT"] + "\n"
    txt+="address-family ipv4\n"
    txt+=" exit-address-family\n"
    txt+="!\n"
    return txt


networkIpsCounter={}
networks={}

# Récupération des données du JSON
configuration = get_data_from_json("JSON/reseau_type.json")
#print(json.dumps(configuration, indent=2))

# Vérification des données
if not check_data(configuration):
    sys.exit()

# Création des Template
with open("Template/template_router_basic.j2") as file:
    baseTemplate = Template(file.read())
with open("Template/template_router_interface.j2") as file:
    interfaceTemplate = Template(file.read())
with open("Template/template_router_ospf.j2") as file:
    ospfTemplate = Template(file.read())
with open("Template/template_router_vrf_forwarding.j2") as file:
    vrfFTemplate = Template(file.read())
with open("Template/template_router_client_bgp.j2") as file:
    bgpClientTemplate = Template(file.read())

for network in configuration["globals"]["networks"]:#prépare à compter les ips déja paramétrées
    networkIpsCounter[network["name"]]=0
    networks[network["name"]]=network

print(networks)

# Rendu Template Basic et Interface pour chaque router
for router in configuration["routers"]:
    rendered_base = baseTemplate.render(name=router["name"])
    configsRouter = []
    configsRouterVPN = []
    # Génération des configurations pour chaque interface
    for interface in router["interface"]:
        if interface["name"] == "loopback" : 
            rendered_interface = interfaceTemplate.render(
                name="loopback 0",
                ip=router["numero"]+"."+router["numero"]+"."+router["numero"]+"."+router["numero"],
                mask="255.255.255.255",
                ospf=router["type"] == "coeur",
                processId=configuration["globals"]["ospf"]["process_id"],
                zoneId=configuration["globals"]["ospf"]["area_id"]
            )  
        else :
            networkIpsCounter[interface["network"]]+=1
            rendered_interface = interfaceTemplate.render(
                name=interface["name"],
                ip=networks[interface["network"]]["ip"]+str(networkIpsCounter[interface["network"]]),
                mask=networks[interface["network"]]["mask"],
                ospf=interface["network"][:5] == "coeur" and router["type"] == "coeur",
                processId=configuration["globals"]["ospf"]["process_id"],
                zoneId=configuration["globals"]["ospf"]["area_id"],
                vrf_f=interface["network"][:5] == "clien" and router["type"] == "coeur",
                name_vrf=extract_string(interface["network"])
            )
        configsRouter.append(rendered_interface+"\n")

    # Génération de la configuration OSPF du router
    if router["type"]=="coeur":
        rendered_ospf = ospfTemplate.render(
            processId=configuration["globals"]["ospf"]["process_id"],
            id=router["numero"]
        )
        configsRouter.append(rendered_ospf)

    # Génération de la configuration BGP du router
    if router["type"] == "coeur":
        if "bgpConfig" in router:
            print("bgpConfig exists " + router["name"])
            configsRouter.append(bgp(configuration["globals"]["bgp"]["ASnumber"], router["bgpConfig"]["neighbors"]))
        else:
            print("bgpConfig doesn't exists " + router["name"])
    elif router["type"] == "client":
        for index, neighbor in enumerate(router["bgpConfig"]["neighbors"]):
            rendered_client_bgp = bgpClientTemplate.render(
                as_number = router["bgpConfig"]["as_number"],
                as_number_neighbor = configuration["globals"]["bgp"]["ASnumber"],
                ip_neighbor = networks[router["interface"][index]["network"]]["ip"]+"1"
            )
        configsRouter.append(rendered_client_bgp)

    # Génération de la configuration VRF du router
    if "vrfConfig" in router:
        print("vrfConfig exists " + router["name"])
        for vrf in router["vrfConfig"]:
            configsRouterVPN.append(create_vrf(vrf["name"], configuration["globals"]["bgp"]["ASnumber"], vrf["routeD"], configuration["globals"]["vrf"]))
    else:
        print("vrfConfig doesn't exists " + router["name"])

    # Génération du fowarding de la VRF du router vers le client
    if "vrfConfig" in router:
        i = 0
        for vrf in router["vrfConfig"]:
            i += 1
            rendered_vfr_f = vrfFTemplate.render(
            name=vrf["name"],
            ip_neighbor=networks[vrf["ip_neighbor"]]["ip"]+str(networkIpsCounter[vrf["ip_neighbor"]]+i),
            as_number_neighbor=vrf["as_number_neighbor"]
        )
        configsRouter.append(rendered_vfr_f)

    # Ecriture des configurations pour chaque routeur
    with open("Configuration/i" + router["numero"] + "_startup-config.cfg", "w") as config_file:
        for configVPN in configsRouterVPN:
            config_file.write(configVPN)
        config_file.write(rendered_base)
        for config in configsRouter:
            config_file.write(config)
        config_file.write("\nend")






