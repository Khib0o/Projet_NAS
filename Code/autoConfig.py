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


# Récupération des données du JSON
configuration = get_data_from_json("JSON/test.json")
print(json.dumps(configuration, indent=2))

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

# Rendu Template Basic et Interface pour chaque router
for router in configuration["routers"]:
    rendered_base = baseTemplate.render(name=router["name"])
    configsRouter = []
    # Génération des configurations pour chaque interface
    for interface in router["interface"]:
        rendered_interface = interfaceTemplate.render(
            name=interface["name"],
            ip=interface["ip"],
            mask="255.255.255.0")
        configsRouter.append(rendered_interface)
    if "bgpConfig" in router:
        print("bgpConfig exists "+router["name"])
        print(bgp(router["bgpConfig"]["ASnumber"],router["bgpConfig"]["neighbors"]))
        configsRouter.append(bgp(router["bgpConfig"]["ASnumber"],router["bgpConfig"]["neighbors"]))
    else:
        print("bgpConfig doesn't exists "+router["name"])

    # Ecriture des configurations pour chaque routeur
    with open("Configuration/i" + router["numero"] + "_startup-config.cfg", "w") as config_file:
        config_file.write(rendered_base)
        for config in configsRouter:
            config_file.write(config)
        config_file.write(rendered_end)

