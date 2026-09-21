#!/usr/bin/env python3

# ########################################################################## #
#                                                                            #
#                                                        :::      ::::::::   #
#   ip_locator.py                                      :+:      :+:    :+:   #
#                                                    +:+ +:+         +:+     #
#   By: nfitahin <nfitahin@student.42antananarivo  +#+  +:+       +#+        #
#                                                +#+#+#+#+#+   +#+           #
#   Created: 2026/09/21 12:49:05 by nfitahin          #+#    #+#             #
#   Updated: 2026/09/21 12:49:05 by nfitahin         ###   ########.fr       #
#                                                                            #
# ########################################################################## #

"""IP Location Finder.

Trouve la localisation approximative d'une adresse IP grâce à l'API
publique ip-api.com.

Exemples :
    python3 ip_locator.py 8.8.8.8
    python3 ip_locator.py 8.8.8.8 1.1.1.1 --json
    python3 ip_locator.py            # demande l'IP en interactif
"""

import argparse
import ipaddress
import json
import sys
from typing import Optional

import requests

API_URL = "http://ip-api.com/json/{ip}"  # le plan gratuit ne supporte pas HTTPS
FIELDS = "status,message,query,country,regionName,city,zip,lat,lon,isp"
DEFAULT_TIMEOUT = 5  # secondes

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_USAGE = 2


class IPLocatorError(Exception):
    """Erreur liée à la validation ou à l'appel de l'API."""


def validate_ip(value: str) -> str:
    """Valide une adresse IPv4/IPv6 publique et la retourne normalisée."""
    try:
        ip = ipaddress.ip_address(value.strip())
    except ValueError:
        raise IPLocatorError(f"Adresse IP invalide : {value!r}")

    if not ip.is_global:
        raise IPLocatorError(
            f"{ip} est une adresse privée ou réservée : "
            "elle ne peut pas être géolocalisée."
        )
    return str(ip)


def get_location(ip: str, timeout: int = DEFAULT_TIMEOUT) -> dict:
    """Interroge l'API et retourne les données de localisation."""
    try:
        response = requests.get(
            API_URL.format(ip=ip),
            params={"fields": FIELDS},
            timeout=timeout,
        )
    except requests.exceptions.Timeout:
        raise IPLocatorError("Délai dépassé : l'API ne répond pas.")
    except requests.exceptions.ConnectionError:
        raise IPLocatorError("Connexion impossible : vérifie ta connexion réseau.")
    except requests.exceptions.RequestException as err:
        raise IPLocatorError(f"Erreur réseau : {err}")

    if response.status_code == 429:
        raise IPLocatorError("Limite de requêtes atteinte (45/min). Réessaie plus tard.")
    if response.status_code != 200:
        raise IPLocatorError(f"Réponse inattendue de l'API (HTTP {response.status_code}).")

    try:
        data = response.json()
    except ValueError:
        raise IPLocatorError("Réponse de l'API illisible (JSON invalide).")

    if data.get("status") != "success":
        raise IPLocatorError(f"Erreur API : {data.get('message', 'inconnue')}")

    return data


def format_location(data: dict) -> str:
    """Formate les données pour l'affichage terminal."""
    rows = (
        ("IP Address", data.get("query")),
        ("Country", data.get("country")),
        ("Region", data.get("regionName")),
        ("City", data.get("city")),
        ("ZIP Code", data.get("zip")),
        ("Latitude", data.get("lat")),
        ("Longitude", data.get("lon")),
        ("ISP", data.get("isp")),
    )
    return "\n".join(
        f"[+] {label:<11}: {value if value not in (None, '') else 'N/A'}"
        for label, value in rows
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Trouve la localisation approximative d'une adresse IP.",
    )
    parser.add_argument("ips", nargs="*", metavar="IP", help="une ou plusieurs adresses IP")
    parser.add_argument("--json", action="store_true", help="sortie au format JSON")
    parser.add_argument(
        "--timeout", type=int, default=DEFAULT_TIMEOUT,
        help=f"délai max en secondes (défaut : {DEFAULT_TIMEOUT})",
    )
    return parser


def main(argv: Optional[list] = None) -> int:
    args = build_parser().parse_args(argv)

    ips = args.ips
    if not ips:
        try:
            ips = [input("Enter an IP address: ")]
        except (EOFError, KeyboardInterrupt):
            print()
            return EXIT_USAGE

    results, had_error = [], False
    for raw_ip in ips:
        try:
            data = get_location(validate_ip(raw_ip), timeout=args.timeout)
        except IPLocatorError as err:
            print(f"[!] {err}", file=sys.stderr)
            had_error = True
            continue

        results.append(data)
        if not args.json:
            print(f"\n{format_location(data)}")

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))

    return EXIT_ERROR if had_error else EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
