Utilisation : 
    - Décompresser l'archive à l'emplacement du projet de manière à avoir dans un même dossier le fichier "autoconfig.py",
    le dossier "src", le projet GNS3 et le fichier conf.json décrivant le réseau

    - Premièrement créer son projet GNS3 et dessiner la topologie et les liaisions

    - Remplir le fichier conf.json

    - Lancer avec python "autoconfig.py"

    - Puis extraire la table de routage en tapant le chiffre 2 avec le clavier

    - Ensuite générer les différents fichiers de configs qui seront rangés dans l'emplacement configs/ On peut les vérifier
    avant de les push dans le projet GNS3

    - Push les fichiers générés dans le projet (Attention, il faut avoir réalisé les deux étapes précédentes)

    - Lancer le projet GNS3 et démarrer les routeurs et tout fonctionne par magie


Remarques :

    - Il faut faire attention à la création du fichier "conf.json" car certains tests ne sont pas implémentés 
    et il est possible d'écrire des bêtises sans que le code ne râle, particulièrement sur les VPNs

    - Nous utilisons le module jinja2, il faut peut-etre l'installer pour faire fonctionner notre code. 
    
    - Notre code est pensé pour fonctionner sur linux. Le lancer sous windows générera sans doute des bugs dûs aux
    appels des fonctions du module os

Bugs connus :

    - Pas de bugs connus