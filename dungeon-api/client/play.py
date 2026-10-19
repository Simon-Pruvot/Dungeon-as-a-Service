"""Client terminal du jeu.

    python client/play.py register --username alice --password secret
    python client/play.py login --username alice --password secret
    python client/play.py create --name Aragorn --classe guerrier --force 6 --agilite 2 --intelligence 2
    python client/play.py look --hero 1
    python client/play.py move --hero 1 --direction nord
    python client/play.py attack --hero 1
    python client/play.py rest --hero 1
"""

import argparse
import json
from pathlib import Path

import requests

API_URL = "http://127.0.0.1:8000"
TOKEN_FILE = Path(".token")


def headers() -> dict:
    if not TOKEN_FILE.exists():
        raise SystemExit("Pas de token : lancez d'abord la commande login.")
    return {"Authorization": f"Bearer {TOKEN_FILE.read_text().strip()}"}


def show(response: requests.Response) -> None:
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="Dungeon as a Service — client terminal")
    sub = parser.add_subparsers(dest="command", required=True)

    for name in ("register", "login"):
        p = sub.add_parser(name)
        p.add_argument("--username", required=True)
        p.add_argument("--password", required=True)

    p = sub.add_parser("create")
    p.add_argument("--name", required=True)
    p.add_argument("--classe", required=True, choices=["guerrier", "mage", "voleur"])
    p.add_argument("--force", type=int, required=True)
    p.add_argument("--agilite", type=int, required=True)
    p.add_argument("--intelligence", type=int, required=True)

    for name in ("look", "attack", "rest"):
        sub.add_parser(name).add_argument("--hero", type=int, required=True)

    p = sub.add_parser("move")
    p.add_argument("--hero", type=int, required=True)
    p.add_argument("--direction", required=True, choices=["nord", "sud", "est", "ouest"])

    args = parser.parse_args()
    hero_url = f"{API_URL}/heroes/{getattr(args, 'hero', '')}"

    if args.command == "register":
        show(requests.post(f"{API_URL}/auth/register", json={"username": args.username, "password": args.password}))
    elif args.command == "login":
        response = requests.post(f"{API_URL}/auth/login", data={"username": args.username, "password": args.password})
        if response.ok:
            TOKEN_FILE.write_text(response.json()["access_token"])
            print("Connecté, token enregistré dans .token")
        else:
            show(response)
    elif args.command == "create":
        body = {
            "nom": args.name,
            "classe": args.classe,
            "force": args.force,
            "agilite": args.agilite,
            "intelligence": args.intelligence,
        }
        show(requests.post(f"{API_URL}/heroes", json=body, headers=headers()))
    elif args.command == "look":
        show(requests.get(f"{hero_url}/room", headers=headers()))
    elif args.command == "move":
        show(requests.post(f"{hero_url}/move", json={"direction": args.direction}, headers=headers()))
    elif args.command == "attack":
        show(requests.post(f"{hero_url}/attack", headers=headers()))
    elif args.command == "rest":
        print("Le héros se repose...")
        show(requests.post(f"{hero_url}/rest", headers=headers()))


if __name__ == "__main__":
    main()
