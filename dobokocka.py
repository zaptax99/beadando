"""
Dice Game Module
================

Ez a modul egy moduláris kockadobó játékot valósít meg. A kódot a
projektfeladathoz igazítottuk a *Szkript nyelvek* tárgyhoz. A
`DiceGame` osztály állítja elő a dobáskocka animációit, kezeli a
dobjáték logikáját, és az eredményeket SQLite adatbázisban tárolja.

Az osztály metódusai az "dp_" monogramot tartalmazzák, de a
projektfeladat követelményei szerint ezeket a metódusokat mindenki
cserélje le a saját monogramjára (például `ab_`, `xy_`), így a
tanár könnyen be tudja azonosítani a saját munkát.

Fő funkciók:

* ``dp_draw_face(number, size)`` – kirajzolja a kocka adott számú arcát.
* ``dp_roll_animation()`` – animált pörgetést valósít meg.
* ``dp_single_roll()`` – végrehajt egy animált dobást és visszaadja az
  eredményt, valamint növeli a dobásszámlálót.
* ``dp_roll_many(count)`` – több dobást hajt végre és visszaadja az
  eredményeket, illetve elmenti azokat az adatbázisba.
* ``dp_get_random(min_val, max_val)`` – véletlen szám generálása egy
  intervallumból. Ezzel szimulálható a véletlenszám API, ha nincs
  külső szolgáltatás.
* ``dp_get_stats()`` – lekéri az összesített statisztikát az
  adatbázisból.

A modul önmagában nem indít el semmilyen GUI-t; a felhasználói
felületet a `main.py` tartalmazza. A modul használatakor a
`DiceGame` osztály példányosítása után hívhatók a metódusok.

"""

from __future__ import annotations

import random
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple

import turtle


@dataclass
class DiceGame:
    """Kockadobó játék logikája és animációja.

    A `DiceGame` osztály a dobások animációját Turtle segítségével
    jeleníti meg, gondoskodik az eredmények számításáról, valamint
    az eredmények SQLite adatbázisban való tárolásáról. A monogram
    ``dp_`` részeket mindenki cserélje le a saját monogramjára.
    """

    db_path: Path = Path("dice.db")

    def __post_init__(self) -> None:
        """Inicializálja az osztály állapotát.

        A dobásszámlálót nullázza, létrehozza az adatbázist, majd
        előkészíti a Turtle felületet. A docstringeket használjuk a
        kód dokumentálására, mivel kommenteket a beadandóban nem
        használunk.
        """
        self.roll_count: int = 0
        self._init_db()
        self._setup_turtle()

    def _init_db(self) -> None:
        """Létrehozza az adatbázist és a táblát, ha még nem létezik."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS kocka (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dobasszam INTEGER,
                egy INTEGER,
                ketto INTEGER,
                harom INTEGER,
                negy INTEGER,
                ot INTEGER,
                hat INTEGER
            )
            """
        )
        conn.commit()
        conn.close()

    def dp_save_results(self, count: int, results: Dict[int, int]) -> None:
        """Eredmények elmentése az adatbázisba.

        ``count`` megadja a dobások számát, a ``results`` pedig egy
        dictionary, ahol a kulcsok a kocka oldalai, az érték pedig a
        dobások gyakorisága.
        """
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO kocka (dobasszam, egy, ketto, harom, negy, ot, hat)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                count,
                results.get(1, 0),
                results.get(2, 0),
                results.get(3, 0),
                results.get(4, 0),
                results.get(5, 0),
                results.get(6, 0),
            ),
        )
        conn.commit()
        conn.close()

    def dp_get_stats(self) -> Dict[int, int]:
        """Lekéri az összesített statisztikát az adatbázisból.

        Visszatér egy dictionaryvel, ahol a kulcsok 1–6, az értékek
        pedig az eddig eltárolt dobások összegei.
        """
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        stats: Dict[int, int] = {i: 0 for i in range(1, 7)}
        for row in cur.execute("SELECT egy, ketto, harom, negy, ot, hat FROM kocka"):
            for idx, val in enumerate(row, start=1):
                stats[idx] += val
        conn.close()
        return stats

    def _setup_turtle(self) -> None:
        """Előkészíti a Turtle grafikus képernyőt és turtle példányt."""
        self.screen = turtle.Screen()
        self.screen.title("Dobókocka Szimulátor 2.0")
        self.screen.bgcolor("lightgreen")
        self.screen.setup(width=600, height=600)
        self.turtle = turtle.Turtle()
        self.turtle.hideturtle()
        self.turtle.speed(0)
        self.turtle.penup()

    def dp_draw_dots(self, positions: Tuple[Tuple[float, float], ...], dot_radius: float, color: str = "black") -> None:
        """Egy vagy több pötty kirajzolása a kocka felületén.

        :param positions: relatív koordináták a turtle aktuális pozíciójához képest
        :param dot_radius: a pötty sugara pixelben
        :param color: a pötty színe
        """
        self.turtle.color(color)
        for x, y in positions:
            self.turtle.goto(x, y)
            self.turtle.pendown()
            self.turtle.begin_fill()
            self.turtle.circle(dot_radius)
            self.turtle.end_fill()
            self.turtle.penup()

    def dp_draw_face(self, number: int, size: float = 200.0) -> None:
        """Kirajzolja a kocka adott számú arcát Turtle-lel.

        ``number`` az 1–6 közötti kockaérték, ``size`` pedig a kocka
        mérete pixelben. A függvény először törli a korábbi rajzot,
        majd fehér háttéren ábrázolja a kockát és a pöttyöket.
        """
        self.turtle.clear()
        half = size / 2
        self.turtle.penup()
        self.turtle.goto(-half, half)
        self.turtle.pendown()
        self.turtle.color("black", "white")
        self.turtle.begin_fill()
        for _ in range(4):
            self.turtle.forward(size)
            self.turtle.right(90)
        self.turtle.end_fill()
        self.turtle.penup()
        self.turtle.color("black")
        offset = size / 4
        positions_map = {
            1: ((0, 0),),
            2: ((-offset, offset), (offset, -offset)),
            3: ((-offset, offset), (0, 0), (offset, -offset)),
            4: ((-offset, offset), (offset, offset), (-offset, -offset), (offset, -offset)),
            5: ((-offset, offset), (offset, offset), (0, 0), (-offset, -offset), (offset, -offset)),
            6: ((-offset, offset), (-offset, 0), (-offset, -offset), (offset, offset), (offset, 0), (offset, -offset)),
        }
        dot_radius = size * 0.05
        self.dp_draw_dots(positions_map[number], dot_radius)

    def dp_roll_animation(self, size: float = 200.0, min_rolls: int = 5, max_rolls: int = 15, delay: float = 0.1) -> None:
        """Animált pörgés: véletlen kocka‑arcok gyors egymásutánban.

        A paraméterek segítségével meghatározható a kocka mérete, a
        villanások száma és az animáció sebessége.
        """
        rolls = random.randint(min_rolls, max_rolls)
        for _ in range(rolls):
            num = random.randint(1, 6)
            self.dp_draw_face(num, size=size)
            time.sleep(delay)

    def dp_single_roll(self, size: float = 200.0) -> int:
        """Végrehajt egy animált dobást és visszaadja a számot.

        :param size: a kocka mérete pixelben
        :return: a dobott szám 1–6 között
        """
        self.dp_roll_animation(size=size)
        result = random.randint(1, 6)
        self.dp_draw_face(result, size=size)
        self.roll_count += 1
        return result

    
    def dp_roll_many(self, count: int, size: float = 200.0) -> Dict[int, int]:
        """Több dobás végrehajtása, eredmények visszaadása és adatbázis mentés.

        :param count: hányat dobjunk
        :param size: a kocka mérete pixelben (csak az utolsó dobást rajzoljuk ki)
        :return: dictionary a dobott oldalak gyakoriságával
        """
        if count <= 0:
            raise ValueError("A dobások száma legyen legalább 1!")
        results: Dict[int, int] = {i: 0 for i in range(1, 7)}
        for _ in range(count):
            num = random.randint(1, 6)
            results[num] += 1
        
        self.dp_roll_animation(size=size)
        final = random.randint(1, 6)
        self.dp_draw_face(final, size=size)
        self.roll_count += count
        
        self.dp_save_results(count, results)
        return results

    
    def dp_get_random(self, min_val: int = 10, max_val: int = 500) -> int:
        """Véletlen szám generálása a megadott tartományban.

        Ez a metódus pótolja a külső API hívást, amely a front-end
        gombnyomásakor meghívható.

        :param min_val: a minimum érték
        :param max_val: a maximum érték
        :return: véletlen egész min_val és max_val között
        """
        return random.randint(min_val, max_val)
