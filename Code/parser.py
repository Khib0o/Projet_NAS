import json
import os
import sys
from jinja2 import Template

# Récupération des données


def getDataFromJson(nameJson):
    # ouvrir le fichier JSON
    if os.path.exists(nameJson):
        with open(nameJson, "r") as json_file:
            data = json.load(json_file)
        return data
    else:
        print("le fichier test.json n'existe pas")

# Validation des données
def checkData(date):
    return True


# Récupération des données du JSON
configuration = getDataFromJson("test.json")
print(json.dumps(configuration, indent=2))

# Vérification des données
if not checkData(configuration):
    sys.exit()

# Création des Template
with open("Template/template_router_basic.txt") as file:
    baseTemplate = Template(file.read())
with open("Template/template_router_interface.txt") as file:
    interfaceTemplate = Template(file.read())
with open("Template/template_router_end.txt") as file:
    endTemplate = Template(file.read())

# Rendu Template basic
rendered_end = endTemplate.render()

for router in configuration["routers"]:
    rendered_base = baseTemplate.render(name=router["name"])   
    configsRouter = []
    for interface in router["interface"]:
        rendered_interface = interfaceTemplate.render(
            name=interface["name"],
            ip=interface["ip"],
            mask="255.255.255.0")
        configsRouter.append(rendered_interface)
    
    with open("Config/i" + router["numero"] + "_startup-config.cfg", "w") as config_file:
        config_file.write(rendered_base)
        for config in configsRouter:
            config_file.write(config)
        config_file.write(rendered_end)
