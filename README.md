# Dungeon as a Service

API FastAPI d'un jeu de rôle rétro (studio Pixel Crypt) : créer un héros, explorer le donjon, combattre les monstres et vaincre la Liche. Le code est dans [dungeon-api/](dungeon-api/).

## Lancer le projet

```bash
cd dungeon-api
python -m venv .venv
.venv\Scripts\Activate.ps1        # macOS / Linux : source .venv/bin/activate
pip install -r requirements.txt
fastapi dev app/main.py
```

Swagger : http://127.0.0.1:8000/docs

## Notre rendu

- **Membres du groupe :** Simon Pruvot, Simon Beausire, Kevin Bura
- **Lien du dépôt Git :** https://github.com/Simon-Pruvot/Dungeon-as-a-Service
- **Palier atteint :** 4
- **Bonus réalisés :**
  - B-1 client terminal : `python client/play.py --help`
  - B-2 classement : `GET /leaderboard`
  - B-3 tests : `python -m pytest` (10 tests)
  - B-5 journalisation des déplacements et des combats
- **Ce qui ne fonctionne pas :** B-4 PostgreSQL non réalisé. Supprimer un ancien `dungeon.db` des paliers 1-2 avant de lancer (nouvelle table `player` et colonne `owner_id`).

## Routes

| Méthode | Route | Rôle |
|---|---|---|
| POST | `/auth/register` | Créer un compte |
| POST | `/auth/login` | Se connecter (JWT) |
| POST | `/heroes` | Créer un héros |
| GET | `/heroes` | Lister ses héros |
| GET | `/heroes/{id}` | Consulter un héros |
| GET | `/heroes/{id}/room` | Décrire la salle |
| POST | `/heroes/{id}/move` | Se déplacer |
| POST | `/heroes/{id}/attack` | Attaquer |
| POST | `/heroes/{id}/rest` | Se reposer (3 s) |
| GET | `/leaderboard` | Classement public |

## Architecture

- `routes/` : couche HTTP uniquement
- `services/` : logique du jeu
- `domain/` : classes métier `Heros`, `Guerrier`, `Mage`, `Voleur`
- `models/` : tables SQLModel `Hero` et `Player`
- `schemas/` : schémas Pydantic d'entrée et de sortie

L'export OpenAPI est dans `dungeon-api/openapi.json`.
