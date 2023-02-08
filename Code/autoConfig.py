import json
import os
import sys
from jinja2 import Template

# Constante globale
mask_loopback = "255.255.255.255"
mask_ip = "255.255.255.0"
ip_loopback = "192.168.255."
ip_reseau = "192.168."
network_ip_counter = {}
networks = {}

# Permet d'extraire le nom du client VPN
def extract_string(s):
    start = s.find("_") + len("_")
    end = s.find("_", start)
    return s[start:end]

# Création automatique @IP
def remove_duplicates(array):
    return list(set(array))

def sort_strings(strings):
    sorted_strings = sorted(strings, key=lambda x: (x[0] != 'P', x[:2] == 'PE', x[:3] == 'CE_', x))
    return sorted_strings   

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

# Fonction de configuration de BGP
def bgp(asnumber, neighbors):
    txt = "\nrouter bgp " + asnumber + "\n"
    for neighbor in neighbors:
        txt += " neighbor "+ip_loopback+neighbor+" remote-as "+asnumber +"\n"
        txt += " neighbor "+ip_loopback+neighbor+" update-source Loopback0\n"
    txt += " no auto-summary\n ! \n address-family vpnv4\n"
    for neighbor in neighbors:
        txt += "  neighbor "+ip_loopback+neighbor+" activate\n"
    txt += "!\n"
    return txt

# Fonction de configuration des VRF
def create_vrf(name, as_number, route_d, vrf_config):
    txt = "!\n!--- " + name + " commands.\n!\n"
    txt += "vrf definition " + name + "\n"
    txt += " rd " + as_number + ":" + route_d + "\n"
    txt += " route-target import " + as_number + \
        ":" + vrf_config[name]["RT"] + "\n"
    txt += " route-target export " + as_number + \
        ":" + vrf_config[name]["RT"] + "\n"
    for color in vrf_config[name]["RT_import"]:
        txt += " route-target export " + as_number + \
            ":" + vrf_config[color]["RT"] + "\n"
    txt += "address-family ipv4\n"
    txt += " exit-address-family\n"
    txt += "!\n"
    return txt

# Récupération des données du JSON
configuration = get_data_from_json("JSON/reseau_type.json")
# print(json.dumps(configuration, indent=2))

# Vérification des données
if not check_data(configuration):
    sys.exit()
    
# Création des adresse IP
links = []
for router in configuration["routers"]:
    for interface in router["interface"]:
        links.append(interface["network"])
# Suppréssion des doublons
links = remove_duplicates(links)
# Trie des liens dans l'ordre P_x, PE_x, CE_vrf_x
links = sort_strings(links)
# Création des différentes adresse
for index, link in enumerate(links):
    network_ip_counter[link] = 0
    networks[link] = { "name": link, "ip": ip_reseau+str(index+1)+"." }

print(networks)
print("\n")
print(network_ip_counter)

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

# prépare à compter les ips déja paramétrées
# for network in configuration["globals"]["networks"]:
#     network_ip_counter[network["name"]] = 0
#     networks[network["name"]] = network

# Rendu Template Basic et Interface pour chaque router
for router in configuration["routers"]:
    numero_router = router["name"][1:]
    rendered_base = baseTemplate.render(name=router["name"])
    configsRouter = []
    configsRouterVPN = []
    # Génération des configurations de loopback
    rendered_interface_loopback = interfaceTemplate.render(
                name="loopback 0",
                ip=ip_loopback + numero_router,
                mask=mask_loopback,
                ospf=router["type"] == "P" or router["type"] == "PE",
                processId=configuration["globals"]["ospf"]["process_id"],
                zoneId=configuration["globals"]["ospf"]["area_id"]
            )
    configsRouter.append(rendered_interface_loopback+"\n")
    
    # Génération des configurations de chaque interface
    for interface in router["interface"]:
        network_ip_counter[interface["network"]]+=1
        rendered_interface = interfaceTemplate.render(
            name=interface["name"],
            ip=networks[interface["network"]]["ip"] + str(network_ip_counter[interface["network"]]),
            mask=mask_ip,
            ospf=interface["network"][0] == "P" and (router["type"] == "P" or router["type"] == "PE"),
            processId=configuration["globals"]["ospf"]["process_id"],
            zoneId=configuration["globals"]["ospf"]["area_id"],
            vrf_f=interface["network"][:2] == "CE" and router["type"] == "PE",
            name_vrf=extract_string(interface["network"])
        )
        configsRouter.append(rendered_interface+"\n")

    # Génération de la configuration OSPF du router
    if (router["type"] == "P" or router["type"] == "PE"):
        rendered_ospf = ospfTemplate.render(
            processId=configuration["globals"]["ospf"]["process_id"],
            id=numero_router
        )
        configsRouter.append(rendered_ospf)

    # Génération de la configuration BGP du router
    if (router["type"] == "P" or router["type"] == "PE"):
        if "bgpConfig" in router:
            print("bgpConfig exists " + router["name"])
            configsRouter.append(bgp(configuration["globals"]["bgp"]["ASnumber"], router["bgpConfig"]["neighbors"]))
        else:
            print("bgpConfig doesn't exists " + router["name"])
    elif router["type"] == "CE":
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
            ip_neighbor=networks[vrf["ip_neighbor"]]["ip"]+str(network_ip_counter[vrf["ip_neighbor"]]+i),
            as_number_neighbor=vrf["as_number_neighbor"]
        )
        configsRouter.append(rendered_vfr_f)

    # Ecriture des configurations pour chaque routeur
    with open("Configuration/i" + numero_router + "_startup-config.cfg", "w") as config_file:
        for configVPN in configsRouterVPN:
            config_file.write(configVPN)
        config_file.write(rendered_base)
        for config in configsRouter:
            config_file.write(config)
        config_file.write("\nend")






