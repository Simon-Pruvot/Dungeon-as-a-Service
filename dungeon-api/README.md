# Dungeon as a Service — starter

Squelette fourni pour le projet bonus du module Python Backend & FastAPI.

## Installation (à faire une seule fois)

Prérequis : Python 3.10 ou plus récent (`python --version`).

```bash
# 1. Créer et activer un environnement virtuel
python -m venv .venv
# Windows (PowerShell) :
.venv\Scripts\Activate.ps1
# macOS / Linux :
source .venv/bin/activate

# 2. Installer les dépendances
pip install -r requirements.txt
```

## Lancer l'API

Depuis la racine du projet (le dossier qui contient `app/`) :

```bash
fastapi dev app/main.py
```

Ouvrez ensuite http://127.0.0.1:8000/docs : la route `GET /health` doit répondre
`{"status": "ok", ...}`. Si c'est le cas, vous êtes prêts.

## Structure

```
app/
  main.py              point d'entrée, branchement des routers
  database.py          connexion SQLite (FOURNI)
  models/              tables SQLModel
  schemas/             schémas Pydantic d'entrée et de sortie
  domain/              classes métier (Heros, Guerrier, Mage, Voleur)
  services/            logique du jeu
    dungeon_map.py     lecture de la carte (FOURNI)
  routes/              routers FastAPI
data/dungeon_map.json  carte du donjon (FOURNI, ne pas modifier)
client/play.py         client terminal (BONUS)
```

## Réinitialiser la partie

Arrêtez le serveur et supprimez le fichier `dungeon.db` : il sera recréé au prochain lancement.
À faire aussi si vous ajoutez une colonne à une table (SQLite ne met pas à jour une table existante).

---

<!-- À COMPLÉTER PAR LE GROUPE AVANT LE RENDU -->

## Notre rendu

- **Membres du groupe :** Simon Pruvot, Simon Beausire, Kevin Bura
- **Lien du dépôt Git :** https://github.com/Simon-Pruvot/Dungeon-as-a-Service
- **Palier atteint :** 4
- **Bonus réalisés :**
  - B-1 client terminal : `python client/play.py --help` (token sauvegardé dans `.token`)
  - B-2 classement : `GET /leaderboard` (public)
  - B-3 tests : `python -m pytest` depuis ce dossier (base SQLite temporaire)
  - B-5 journalisation : déplacements et tours de combat tracés dans la console (logger `dungeon`)
- **Ce qui ne fonctionne pas / difficultés :**
  - B-4 PostgreSQL non réalisé.
  - La clé JWT se règle avec la variable d'environnement `JWT_SECRET_KEY` (valeur par défaut pour le dev).
  - Si un `dungeon.db` des paliers 1-2 existe déjà, il faut le supprimer : la colonne `owner_id` et la table `player` ont été ajoutées au palier 4.
