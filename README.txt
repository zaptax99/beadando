Ez a projekt a Szkript nyelvek tantárgyhoz készült.
A feladat az volt, hogy egy több fájlból álló, objektumorientált programot készítsünk, legyen benne grafika, eseménykezelés, és legalább 1 osztály több metódussal. A tanár kérte azt is, hogy külön modulok legyenek, a metódusok neveiben szerepeljen a monogram, és legyen egy „main” fájl, ahonnan az egész indul.

A program lényege egy dobókocka szimulátor, ami:

kirajzol egy nagy dobókockát Turtle-lel,

animált pörgést csinál (gyorsan villogó számok),

végül megáll egy véletlen számon,

számolja a dobásokat és menti az adatbázisba, van játék mód is: a felhasználó és a „robot” is dob egyet, és kiírja ki nyert.

A projekt felépítése:

main.py
Innen indul az egész program.
Itt van a menü és a felhasználói rész: mit szeretnél csinálni (dobás, statisztika, játék mód stb.).
A main a backend és a dobokocka modul funkcióit hívja meg.

dobokocka.py
Ez a grafikus rész (Turtle).
Itt rajzolódik ki maga a kocka → nagy fehér négyzet + fekete pöttyök.
Van benne metódus a pöttyök elhelyezésére, teljes kocka kirajzolására és az animációra.

backend.py
Ez a logikai rész és az adatkezelés.
Van benne a DiceGame osztály (az osztály neve és a metódusok tartalmazzák a monogramot).
Itt történik:

véletlen szám generálása (1–6),

statisztika frissítése,

többszörös dobás kezelése,

játék logika (user vs robot),

és ha szükséges: API-s végpontok (Flask) is vannak hozzá.

README.txt
(Ez a mostani fájl.)

A program futtatása:

A mappában legyen minden fájl: main.py, backend.py, dobokocka.py, README.txt

Python 3 kell hozzá.

Indítás:
python main.py

A konzolos menüben lehet választani:

egyszeri dobás (animációval),

statisztika megtekintése,

játék mód,

kilépés.

A Turtle ablakban megjelenik a dobókocka, és minden dobás után frissül a grafika is.