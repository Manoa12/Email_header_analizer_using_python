#!/usr/bin/env python3

# ########################################################################## #
#                                                                            #
#                                                        :::      ::::::::   #
#   README.md                                          :+:      :+:    :+:   #
#                                                    +:+ +:+         +:+     #
#   By: nfitahin <nfitahin@student.42antananarivo  +#+  +:+       +#+        #
#                                                +#+#+#+#+#+   +#+           #
#   Created: 2026/09/21 12:48:50 by nfitahin          #+#    #+#             #
#   Updated: 2026/09/21 12:48:50 by nfitahin         ###   ########.fr       #
#                                                                            #
# ########################################################################## #

# IP Location Finder

Outil en ligne de commande pour trouver la localisation **approximative** d'une adresse IP, en Python, via l'API [ip-api.com](https://ip-api.com).

## Fonctionnalités

- Géolocalisation d'une ou plusieurs adresses IP (IPv4 et IPv6)
- Validation de l'adresse avant l'appel réseau (module `ipaddress`)
- Refus des adresses privées ou réservées (`192.168.x.x`, `10.x.x.x`, `127.0.0.1`…)
- Gestion des erreurs : timeout, réseau coupé, limite de requêtes, réponse invalide
- Sortie lisible dans le terminal ou au format JSON (`--json`)
- Codes de retour exploitables dans des scripts
- Tests unitaires (sans appel réseau réel)

## Installation

```bash
git clone <url-du-repo>
cd ip-location-finder
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Prérequis : Python 3.8+.

## Utilisation

```bash
# Une IP
python3 ip_locator.py 8.8.8.8

# Plusieurs IP
python3 ip_locator.py 8.8.8.8 1.1.1.1

# Sortie JSON
python3 ip_locator.py 8.8.8.8 --json

# Timeout personnalisé (secondes)
python3 ip_locator.py 8.8.8.8 --timeout 10

# Mode interactif (sans argument)
python3 ip_locator.py
```

### Exemple de sortie

```
[+] IP Address : 8.8.8.8
[+] Country    : United States
[+] Region     : California
[+] City       : Mountain View
[+] ZIP Code   : 94043
[+] Latitude   : 37.4056
[+] Longitude  : -122.0775
[+] ISP        : Google LLC
```

### Codes de retour

| Code | Signification |
|------|---------------|
| `0` | Succès |
| `1` | Au moins une IP a échoué (invalide, privée, erreur API/réseau) |
| `2` | Usage incorrect (entrée interactive annulée) |

## Tests

```bash
python3 -m unittest -v
```

## Limites et bonnes pratiques

- La géolocalisation IP est **approximative** : elle indique en général la ville ou la région du fournisseur d'accès, pas l'adresse exacte d'une personne.
- Le plan gratuit d'ip-api.com est limité à **45 requêtes par minute**, en **HTTP uniquement** (pas de HTTPS) et réservé à un usage **non commercial**. Pour un usage en production, prends un plan payant ou un autre fournisseur.
- Ne pas envoyer d'adresses IP sensibles à un service tiers sans y être autorisé.

## Structure

```
ip-location-finder/
├── ip_locator.py
├── test_ip_locator.py
├── requirements.txt
├── .gitignore
└── README.md
```
