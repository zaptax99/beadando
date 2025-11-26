"""Egyszerű Flask alapú háttérszolgáltatás a Dobókocka‑szimulátorhoz.

Ez a modul egy minimalista API-t valósít meg a ``Flask`` könyvtár
segítségével. A célja az, hogy a ``main.py`` alkalmazás gombjai
keresztül lehessen véletlen számot vagy többszörös kockadobást
kérni. A modul feltételezi, hogy a ``dobokocka.DiceGame`` osztály
elérhető ugyanabban a könyvtárban.

A szolgáltatás két végpontot definiál:

* ``/random`` – Visszaad egy véletlen egész számot a ``min`` és
  ``max`` paraméterek alapján (alapértelmezés: 1–6).
* ``/roll/<count>`` – ``count`` darab dobást hajt végre, az
  eredményeket elmenti az adatbázisba, és a gyakoriságokat JSON
  formában visszaadja. Tartalmaz egy ``final`` kulcsot is az
  utolsó dobott értékkel.

Futtatáshoz telepíteni kell a ``flask`` csomagot. A szerver
indítása: ``python backend.py`` – a HTTP szerver alapértelmezés
szerint az ``localhost:5000`` címen fog hallgatni.
"""

from __future__ import annotations

import random
from typing import Dict

from flask import Flask, jsonify, request

from dobokocka import DiceGame


app = Flask(__name__)

# Létrehozunk egy globális DiceGame példányt
game = DiceGame()


@app.route("/random")
def random_number() -> str:
    """Véletlen számot ad vissza JSON formátumban.

    Paraméterek:
    ``min``: minimum érték (opcionális, alapértelmezés 1)
    ``max``: maximum érték (opcionális, alapértelmezés 6)
    """
    try:
        min_val = int(request.args.get("min", 1))
        max_val = int(request.args.get("max", 6))
    except ValueError:
        min_val, max_val = 1, 6
    number = random.randint(min_val, max_val)
    return jsonify({"number": number})


@app.route("/roll/<int:count>")
def roll_many(count: int) -> str:
    """Többszörös kockadobás API végpont.

    ``count`` darab dobást hajt végre, a gyakoriságokat tartalmazó
    dictionaryt JSON-ként adja vissza. Az utolsó dobást ``final``
    kulcsban szerepelteti.
    """
    if count <= 0:
        return jsonify({"error": "count must be positive"}), 400
    results: Dict[int, int] = {i: 0 for i in range(1, 7)}
    for _ in range(count):
        num = random.randint(1, 6)
        results[num] += 1
    # Rajzoljuk ki az utolsó dobást animációval (opcionális)
    # game.dp_roll_animation()  # túl lassú lehet API-n keresztül
    final_value = max(results, key=results.get)
    game.dp_save_results(count, results)
    response = dict(results)
    response["final"] = final_value
    return jsonify(response)


@app.route("/stats")
def stats() -> str:
    """Statisztika végpont: az adatbázisban tárolt dobások összesítése."""
    stats_data = game.dp_get_stats()
    return jsonify(stats_data)


if __name__ == "__main__":
    # A debug opciót kikapcsoljuk a projektfeladat során
    app.run(host="127.0.0.1", port=5000, debug=False)