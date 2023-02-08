# Readme

# Projet_NAS

## V_1_Opti_v1

Cette version marche dans tous les cas, mais le JSON est long et pas optimisé

Exemple de JSON

<aside>
reseau_type.json : 4P - 4PE - 2CE - 1 Client

reseau_type_2.json : 4P - 4PE - 4CE - 2 Client (Partagé car un maison mère)

reseau_type_3.json : 4P - 4PE - 6CE - 3 Client  (Semi-partagé car un maison mère)
</aside>

### Etape de mise en place

1. Crée son projet GNS3 (Router + Link)
2. Crée le fichier JSON adapté au projet GNS3
3. Crée la correspondance avec “checkConfigGNS3.py” (bien changer le chemin du projet)
4. Crée les fichier de configuration avec “autoConfig.py” (bien changer le nom du JSON d’entrée)
5. Déplacer les fichier de configuration avec “autoMove.py” (bien changer le chemin du projet)
6. Tester

## Exemple de JSON

### RT des VRF

blue parle avec blue, red et green

red parle avec red et blue

green parle avec green et blue

```json
"vrf": {
          "red": {
              "RT": "100",
              "RT_import": [
                  "blue"
              ]
          },
          "blue": {
              "RT": "200",
              "RT_import": [
                  "red",
                  "green"
              ]
          },
          "green": {
              "RT": "300",
              "RT_import": [
                  "blue"
              ]
          }
      }
```

### P

Routeur P R1, 4 interface (1 loopback + 3 lien3), OSPF + MPLS + LDP

```json
{
    "name": "R1",
    "type": "P",
    "interface": [
        {
            "name": "g1/0",
            "network": "P_1"
        },
        {
            "name": "g2/0",
            "network": "P_4"
        },
        {
            "name": "g3/0",
            "network": "PE_5"
        }
    ]
}
```

### PE

Router PE R6, 3 interface (1 loopback + 2 liens), OSPF + MPLS + LDP, BGP avec les autres PE (192.168.255.X, X=[5,7,8]), une VRF pour le client blue (AS = 3)

```json
{
        "name": "R6",
        "type": "PE",
        "interface": [
            {
                "name": "g1/0",
                "network": "CE_blue_1"
            },
            {
                "name": "g3/0",
                "network": "PE_6"
            }
        ],
        "bgpConfig": {
            "neighbors": [
                "5",
                "7",
                "8"
            ]
        },
        "vrfConfig": [
            {
                "name": "blue",
                "routeD": "20",
                "ip_neighbor": "CE_blue_1",
                "as_number_neighbor": "3"
            }
        ]
    }
```

### CE

Routeur CE R10, connecter à R8 en g1/0 (lien CE_blue_2), numéro d’AS 5

```json
{
      "name": "R10",
      "type": "CE",
      "interface": [
          {
              "name": "g1/0",
              "network": "CE_blue_2"
          }
      ],
      "bgpConfig": {
          "as_number": 5,
          "neighbors": [
              "8"
          ]
      }
  }
```

Attention bien placé les interface et les neighbor dans le même ordre si CE relier à plusieurs PE
