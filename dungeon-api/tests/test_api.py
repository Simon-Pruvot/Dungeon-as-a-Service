import os
import tempfile
import uuid

os.environ["DATABASE_URL"] = f"sqlite:///{tempfile.gettempdir()}/dungeon_test_{uuid.uuid4().hex}.db"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.domain.heros import Guerrier, Mage, Voleur  # noqa: E402
from app.main import app  # noqa: E402

GUERRIER = {"nom": "Aragorn", "classe": "guerrier", "force": 6, "agilite": 2, "intelligence": 2}


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def auth_headers(client: TestClient) -> dict:
    username = f"joueur_{uuid.uuid4().hex[:8]}"
    client.post("/auth/register", json={"username": username, "password": "secret"})
    token = client.post("/auth/login", data={"username": username, "password": "secret"}).json()
    return {"Authorization": f"Bearer {token['access_token']}"}


def create_hero(client: TestClient, headers: dict, **overrides) -> dict:
    response = client.post("/heroes", json={**GUERRIER, **overrides}, headers=headers)
    assert response.status_code == 201
    return response.json()


def test_domaine():
    assert Guerrier(6, 2, 2).calculer_degats() == (14, False)
    assert Guerrier(6, 2, 2).pv_max == 32
    assert Guerrier(6, 2, 2).subir_degats(1) == 1
    assert Mage(2, 2, 6).calculer_degats() == (19, False)
    assert Voleur(2, 6, 2).calculer_degats()[0] in (14, 28)


def test_creation_heros(client):
    hero = create_hero(client, auth_headers(client))
    assert hero["salle_actuelle"] == "entree"
    assert hero["pv"] == hero["pv_max"] == 32
    assert hero["est_vivant"] and not hero["en_combat"]
    assert "owner_id" not in hero and "monstre_pv" not in hero


def test_creation_invalide_422(client):
    headers = auth_headers(client)
    for invalid in ({"force": 8, "agilite": 5}, {"nom": "Al"}, {"classe": "pretre"}, {"force": 0}):
        assert client.post("/heroes", json={**GUERRIER, **invalid}, headers=headers).status_code == 422


def test_sans_token_401(client):
    assert client.get("/heroes").status_code == 401
    assert client.get("/heroes", headers={"Authorization": "Bearer faux"}).status_code == 401


def test_heros_inconnu_404(client):
    response = client.get("/heroes/9999", headers=auth_headers(client))
    assert response.status_code == 404
    assert response.json()["detail"]["error"] == "HERO_NOT_FOUND"


def test_deplacement_et_no_exit(client):
    headers = auth_headers(client)
    hero = create_hero(client, headers)
    assert client.post(f"/heroes/{hero['id']}/move", json={"direction": "haut"}, headers=headers).status_code == 422
    response = client.post(f"/heroes/{hero['id']}/move", json={"direction": "nord"}, headers=headers)
    assert response.json()["id"] == "hall"
    client.post(f"/heroes/{hero['id']}/move", json={"direction": "nord"}, headers=headers)
    response = client.post(f"/heroes/{hero['id']}/move", json={"direction": "est"}, headers=headers)
    assert response.status_code == 409
    assert response.json()["detail"]["error"] == "IN_COMBAT"


def test_no_exit_400(client):
    headers = auth_headers(client)
    hero = create_hero(client, headers)
    response = client.post(f"/heroes/{hero['id']}/move", json={"direction": "est"}, headers=headers)
    assert response.status_code == 400
    assert response.json()["detail"]["error"] == "NO_EXIT"


def test_combat_gobelin_et_repos(client):
    headers = auth_headers(client)
    hero = create_hero(client, headers)
    hid = hero["id"]
    assert client.post(f"/heroes/{hid}/attack", headers=headers).json()["detail"]["error"] == "NO_MONSTER"
    client.post(f"/heroes/{hid}/move", json={"direction": "nord"}, headers=headers)
    room = client.post(f"/heroes/{hid}/move", json={"direction": "ouest"}, headers=headers).json()
    assert room["monstre"]["pv"] == 12
    assert client.post(f"/heroes/{hid}/rest", headers=headers).status_code == 409

    tour = client.post(f"/heroes/{hid}/attack", headers=headers).json()
    assert tour == {
        "degats_infliges": 14, "critique": False, "degats_subis": 0, "pv_heros": 32,
        "pv_monstre": 0, "issue": "monstre_vaincu", "or_gagne": 10, "victoire": False,
    }
    hero = client.get(f"/heroes/{hid}", headers=headers).json()
    assert hero["or_"] == 10 and not hero["en_combat"]
    assert client.post(f"/heroes/{hid}/rest", headers=headers).json()["pv"] == 32


def test_heros_d_un_autre_joueur_403(client):
    hero = create_hero(client, auth_headers(client))
    other = auth_headers(client)
    response = client.post(f"/heroes/{hero['id']}/move", json={"direction": "nord"}, headers=other)
    assert response.status_code == 403
    assert response.json()["detail"]["error"] == "NOT_YOUR_HERO"
    assert client.get("/heroes", headers=other).json() == []


def test_victoire_contre_la_liche(client):
    headers = auth_headers(client)
    hid = create_hero(client, headers, nom="Merlin", classe="mage", force=2, agilite=2, intelligence=6)["id"]

    def move(direction):
        return client.post(f"/heroes/{hid}/move", json={"direction": direction}, headers=headers)

    def fight():
        while (tour := client.post(f"/heroes/{hid}/attack", headers=headers).json())["issue"] == "en_cours":
            pass
        assert tour["issue"] == "monstre_vaincu"
        return tour

    move("nord"), move("nord"), fight()
    move("nord"), fight()
    move("est"), client.post(f"/heroes/{hid}/rest", headers=headers)
    move("ouest"), fight()
    move("nord")
    assert client.post(f"/heroes/{hid}/rest", headers=headers).status_code == 409
    assert fight()["victoire"] is True
    assert client.get("/leaderboard").json()[0]["id"] == hid
