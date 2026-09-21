#!/usr/bin/env python3

# ########################################################################## #
#                                                                            #
#                                                        :::      ::::::::   #
#   README.md                                          :+:      :+:    :+:   #
#                                                    +:+ +:+         +:+     #
#   By: nfitahin <nfitahin@student.42antananarivo  +#+  +:+       +#+        #
#                                                +#+#+#+#+#+   +#+           #
#   Created: 2026/09/21 12:36:32 by nfitahin          #+#    #+#             #
#   Updated: 2026/09/21 12:36:32 by nfitahin         ###   ########.fr       #
#                                                                            #
# ########################################################################## #

# Email Header Analyzer

Petit outil en Python pour analyser le routage et l'authentification d'un email à partir de ses en-têtes bruts.

## Fonctionnalités

- Extrait les champs principaux : `From`, `To`, `Subject`, `Date`, `Return-Path`, `Message-ID`
- Affiche tous les sauts `Received` (chemin de l'email, de l'expéditeur au destinataire)
- Vérifie les résultats **SPF**, **DKIM** et **DMARC**
- Gère les en-têtes répartis sur plusieurs lignes (dépliage automatique)
- Aucune installation de bibliothèque externe

## Prérequis

- Python 3.8 ou supérieur (bibliothèque standard uniquement)

## Utilisation

1. Récupérer l'en-tête brut de l'email (dans votre client mail : « Afficher l'original » / « Voir les en-têtes »).
2. L'enregistrer dans un fichier texte, par exemple `header.txt`.
3. Lancer :

```bash
python3 email_analyzer.py header.txt
```

Un fichier d'exemple est fourni :

```bash
python3 email_analyzer.py sample_header.txt
```

## Exemple de sortie

```
=== EMAIL HEADER ANALYSIS ===
From        : alerts@example.com
To          : user@example.net
Subject     : Security Alert
Date        : Tue, 08 Sep 2026 10:20:14 +0000
Return-Path : <bounce@example.com>
Message-ID  : <abc123@example.com>

Authentication Results:
SPF   : PASS
DKIM  : PASS
DMARC : PASS

Received Hops:
1. from mail.example.com (mail.example.com [198.51.100.5]) by mx.example.net ...
2. from mx.example.net (mx.example.net [192.0.2.10]) by inbound.mailserver.com ...

[+] Header analysis completed.
```

## Comment ça marche

1. Lecture du fichier d'en-têtes avec le module `email` de la bibliothèque standard.
2. Extraction des champs principaux.
3. Lecture de `Authentication-Results` (avec repli sur `Received-SPF`) pour SPF, DKIM et DMARC.
4. Affichage des sauts `Received` dans l'ordre chronologique.

## Interprétation des résultats

| Valeur | Signification |
|--------|---------------|
| `PASS` | La vérification a réussi |
| `FAIL` / `SOFTFAIL` | La vérification a échoué (email potentiellement usurpé) |
| `NEUTRAL` | Le domaine ne se prononce pas |
| `NONE` | Aucune information trouvée dans les en-têtes |

## Limites

- Les résultats SPF/DKIM/DMARC sont **lus** dans les en-têtes ajoutés par le serveur de réception ; l'outil ne refait pas les vérifications DNS.
- Un en-tête peut être falsifié : les lignes `Received` ajoutées avant votre serveur de réception ne sont pas fiables.

## Structure

```
email-header-analyzer/
├── email_analyzer.py
├── sample_header.txt
└── README.md
```
