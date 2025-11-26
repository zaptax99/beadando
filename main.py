"""Fő indító modul a Dobókocka‑szimulátorhoz.

Ez a modul definiál egy ``DiceAppPF`` nevű osztályt, amely a
``tkinter`` könyvtár segítségével grafikus felületet biztosít a
``dobokocka.DiceGame`` osztály funkcionalitásához. A névben a "PF" a
monogram példa; cseréld le a saját monogramodra, hogy a tanár
beazonosíthassa a munkádat.

A felhasználó gombokkal indíthat helyi dobást, kérhet véletlen
számot (API vagy helyi), indíthat több dobást egyszerre, megtekintheti
a statisztikát, valamint kiléphet az alkalmazásból. Ha az API
nincs elérhető (vagy nem fut), a program a beépített véletlenszám
generátort használja.
"""

from __future__ import annotations

import json
import tkinter as tk
from tkinter import messagebox
from typing import Dict
import urllib.request
import urllib.error

from dobokocka import DiceGame


class DiceAppPF(DiceGame):
    """Grafikus felület a kockadobó játékhoz (tkinter).

    Örökli a ``dobokocka.DiceGame`` osztályt, így a Turtle
    animációk és az adatbázis-kezelés már rendelkezésre áll. A
    grafikus felületen keresztül vezérli a dobásokat és jeleníti meg
    az eredményeket. A gombnyomások eseménykezelése megfelel a
    projektfeladat követelményeinek.
    """

    def __init__(self, master: tk.Tk) -> None:
        super().__init__()
        self.master = master
        master.title("Dobókocka Applikáció")

        # Helyi dobás gomb és eredmény címke
        tk.Button(master, text="Helyi dobás", command=self.pf_local_roll).grid(row=0, column=0, padx=5, pady=5)
        self.local_label = tk.Label(master, text="", width=10)
        self.local_label.grid(row=0, column=1, padx=5, pady=5)

        # API véletlen szám lekérés gomb és eredmény
        tk.Button(master, text="API véletlen", command=self.pf_api_random).grid(row=1, column=0, padx=5, pady=5)
        self.api_random_label = tk.Label(master, text="", width=10)
        self.api_random_label.grid(row=1, column=1, padx=5, pady=5)

        # Többszörös dobás: beviteli mező és API dobás gomb + eredmény
        tk.Label(master, text="Dobások száma:").grid(row=2, column=0, padx=5, pady=5)
        self.count_entry = tk.Entry(master, width=5)
        self.count_entry.insert(0, "5")
        self.count_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Button(master, text="API dobás", command=self.pf_api_roll).grid(row=3, column=0, padx=5, pady=5)
        self.api_roll_label = tk.Label(master, text="", width=10)
        self.api_roll_label.grid(row=3, column=1, padx=5, pady=5)

        # Statisztika gomb
        tk.Button(master, text="Statisztika", command=self.pf_show_stats).grid(row=4, column=0, padx=5, pady=5)

        # Kilépés gomb
        tk.Button(master, text="Kilépés", command=master.destroy).grid(row=5, column=0, padx=5, pady=5)

    # --- Eseménykezelők ---
    def pf_local_roll(self) -> None:
        """Helyi (animált) kockadobás végrehajtása.

        Meghívja a szülőosztály ``dp_single_roll`` metódusát és
        frissíti a címkét az eredménnyel.
        """
        number = self.dp_single_roll()
        self.local_label.config(text=str(number))

    def pf_api_random(self) -> None:
        """Véletlen szám lekérése a háttértől vagy helyben.

        Az alkalmazás először megpróbálja a ``backend.py`` által
        biztosított API-t hívni (http://localhost:5000/random?min=1&max=6).
        Ha a kapcsolat sikertelen vagy nem érkezik válasz, a program
        helyi véletlenszám-generátort használ.
        """
        url = "http://localhost:5000/random?min=1&max=6"
        number = None
        try:
            with urllib.request.urlopen(url, timeout=2) as resp:
                data = json.loads(resp.read().decode())
                number = data.get("number")
        except (urllib.error.URLError, ValueError, TimeoutError):
            pass
        if number is None:
            number = self.dp_get_random(1, 6)
        self.api_random_label.config(text=str(number))

    def pf_api_roll(self) -> None:
        """Többszörös dobás (API vagy helyi).

        Beolvassa a felhasználó által megadott dobások számát. Először
        megpróbálja az API-t hívni (http://localhost:5000/roll/<count>),
        majd hiba esetén a helyi ``dp_roll_many`` metódust használja.
        Az eredmények közül az utolsó dobott számot jeleníti meg.
        """
        try:
            count = int(self.count_entry.get())
        except ValueError:
            messagebox.showerror("Hiba", "Kérem adjon meg egy egész számot a dobások számaként!")
            return
        if count <= 0:
            messagebox.showerror("Hiba", "A dobások száma legyen pozitív!")
            return
        # Próbálkozás API-val
        url = f"http://localhost:5000/roll/{count}"
        final_number: int | None = None
        try:
            with urllib.request.urlopen(url, timeout=3) as resp:
                data = json.loads(resp.read().decode())
                # A válasz tartalmazhatja a gyakoriságokat. Vegyük az utolsó dobást.
                # Ha 'final' kulcs van, használjuk, különben számoljuk ki a legtöbbször előforduló számot.
                final_number = data.get("final")
                if final_number is None and isinstance(data, dict):
                    # Válasszuk a legtöbbször dobott értéket
                    final_number = max(data, key=data.get) if data else None
        except (urllib.error.URLError, ValueError, TimeoutError):
            pass
        # Ha API nem adott választ, végezzük el helyben a dobásokat
        if final_number is None:
            results: Dict[int, int] = self.dp_roll_many(count)
            # Válasszuk a legtöbbször dobott értéket
            final_number = max(results, key=results.get)
        self.api_roll_label.config(text=str(final_number))

    def pf_show_stats(self) -> None:
        """Statisztika megjelenítése párbeszédablakban.

        Lekéri az összesített statisztikát az adatbázisból és
        megjeleníti egy üzenetboxban.
        """
        stats = self.dp_get_stats()
        stat_lines = [f"{k}: {v}" for k, v in sorted(stats.items())]
        message = "\n".join(stat_lines)
        messagebox.showinfo("Statisztika", message or "Nincs elérhető adat.")


def main() -> None:
    """Alkalmazás indítása.

    Létrehozza a ``Tk`` ablakot és a ``DiceAppPF`` példányt, majd
    belép az eseményhurokba.
    """
    root = tk.Tk()
    app = DiceAppPF(root)
    root.mainloop()


if __name__ == "__main__":
    main()