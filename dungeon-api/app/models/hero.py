"""Table des heros"""

from sqlmodel import Field, SQLModel


class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)  
    nom: str
    classe: str
    force: int
    agilite: int
    intelligence: int
    pv: int
    pv_max: int
    salle_actuelle: str
    or_: int = 0
    monstre_pv: int | None = None  
    victoire: bool = False
