#!/usr/bin/env python3

# ########################################################################## #
#                                                                            #
#                                                        :::      ::::::::   #
#   email_analyzer.py                                  :+:      :+:    :+:   #
#                                                    +:+ +:+         +:+     #
#   By: nfitahin <nfitahin@student.42antananarivo  +#+  +:+       +#+        #
#                                                +#+#+#+#+#+   +#+           #
#   Created: 2026/09/14 12:40:51 by nfitahin          #+#    #+#             #
#   Updated: 2026/09/14 12:40:51 by nfitahin         ###   ########.fr       #
#                                                                            #
# ########################################################################## #


"""Email Header Analyzer.

Analyse les en-têtes bruts d'un email : champs principaux, résultats
d'authentification (SPF, DKIM, DMARC) et chemin de routage (Received).

Bibliothèque standard uniquement (Python 3.8+).
"""

import re
import sys
from email import policy
from email.parser import HeaderParser
from pathlib import Path

MAIN_FIELDS = (
    "From",
    "To",
    "Subject",
    "Date",
    "Return-Path",
    "Message-ID",
)

AUTH_METHODS = ("spf", "dkim", "dmarc")

# Exemples : "spf=pass", "dkim=fail", "dmarc=none"
AUTH_RESULT_RE = re.compile(r"\b(spf|dkim|dmarc)\s*=\s*([a-z]+)", re.IGNORECASE)
# Anciens en-têtes : "Received-SPF: pass (...)"
RECEIVED_SPF_RE = re.compile(r"^\s*([a-z]+)", re.IGNORECASE)


def read_headers(path: str):
    """Lit un fichier d'en-têtes et retourne un objet Message."""
    text = Path(path).read_text(encoding="utf-8", errors="ignore")
    # policy.default gère le dépliage des en-têtes sur plusieurs lignes
    return HeaderParser(policy=policy.default).parsestr(text)


def parse_main_fields(msg) -> dict:
    """Extrait les champs principaux (valeur 'N/A' si absent)."""
    return {field: str(msg[field]).strip() if msg[field] else "N/A"
            for field in MAIN_FIELDS}


def check_authentication(msg) -> dict:
    """Retourne le résultat de SPF, DKIM et DMARC.

    Valeurs possibles : PASS, FAIL, SOFTFAIL, NEUTRAL, NONE, etc.
    'NONE' est utilisé quand l'information est absente des en-têtes
    (absent n'est pas la même chose qu'un échec).
    """
    results = {method.upper(): "NONE" for method in AUTH_METHODS}

    # 1) Authentication-Results (peut apparaître plusieurs fois)
    for header in msg.get_all("Authentication-Results", []):
        for method, value in AUTH_RESULT_RE.findall(str(header)):
            key = method.upper()
            # On garde le premier résultat trouvé (le plus récent)
            if results[key] == "NONE":
                results[key] = value.upper()

    # 2) Repli sur Received-SPF si SPF est toujours inconnu
    if results["SPF"] == "NONE":
        received_spf = msg.get("Received-SPF")
        if received_spf:
            match = RECEIVED_SPF_RE.match(str(received_spf))
            if match:
                results["SPF"] = match.group(1).upper()

    return results


def get_received_hops(msg) -> list:
    """Retourne les sauts 'Received' dans l'ordre chronologique.

    Dans un email, le saut le plus récent est en haut ; on inverse
    donc la liste pour lire le trajet de l'expéditeur au destinataire.
    """
    hops = [" ".join(str(h).split()) for h in msg.get_all("Received", [])]
    return list(reversed(hops))


def format_report(fields: dict, auth: dict, hops: list) -> str:
    """Construit le rapport texte."""
    lines = ["", "=== EMAIL HEADER ANALYSIS ==="]
    for key, value in fields.items():
        lines.append(f"{key:<12}: {value}")

    lines += ["", "Authentication Results:"]
    for key, value in auth.items():
        lines.append(f"{key:<6}: {value}")

    if hops:
        lines += ["", "Received Hops:"]
        for i, hop in enumerate(hops, 1):
            lines.append(f"{i}. {hop}")
    else:
        lines += ["", "Received Hops: aucun trouvé"]

    lines += ["", "[+] Header analysis completed."]
    return "\n".join(lines)


def analyze_email(path: str) -> None:
    msg = read_headers(path)
    fields = parse_main_fields(msg)
    auth = check_authentication(msg)
    hops = get_received_hops(msg)
    print(format_report(fields, auth, hops))


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python email_analyzer.py <header_file>")
        return 1
    try:
        analyze_email(sys.argv[1])
    except FileNotFoundError:
        print(f"Erreur : fichier introuvable : {sys.argv[1]}")
        return 1
    except OSError as err:
        print(f"Erreur de lecture : {err}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
