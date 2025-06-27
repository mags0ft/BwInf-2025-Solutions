# Aufgabe 5: Das ägyptische Grabmal

**Die Abgabe ist nicht vollständig gelöst, und wir sind uns der Limitationen bewusst.** Wir haben uns dennoch entschieden, diese Lösung ebenfalls abzugeben, da sie trotzdessen sinnvollen Code enthält. Weitere Erläuterungen gibt es unten.

## Programmnutzung:

So verwendet man das Programm im Terminal:

```bash
$ python3 ./grabmal.py NAME_DER_EINGABEDATEI
```

Beispiel:

```bash
$ python3 ./grabmal.py ./grabmal0.txt
```

## Grundgedanken und Programmablauf

Damit wir den schnellsten Weg finden können, haben wir uns für eine simple, aber effektive Nachstellung des Szenarios in Code entschieden. Dabei springen wir immer wenn möglich weiter, damit wir keine Zeit verschwenden. Obwohl wir darin eigentlich Meister\*innen sind. Aber naja, wie dem auch sei.

1. wieder einmal: Datei einlesen!
    1. in einzelne Zeilen aufspalten, für jede Zeile:
        1. wenn erste Zeile oder leere Zeile: ignorieren
        2. den einzelnen Wert in der Zeile versuchen, in einen `int` umzuwandeln.
        3. wenn dies nicht möglich ist: Fehler an stderr ausgeben und abbrechen
    2. die zwischengespeicherten `int`s zurückgeben

2. Das Szenario in Ruhe simulieren:
    1. wir schreiten in der Zeit immer so schnell voran, wie es nötig ist, damit der nächste Abschnitt sich öffnet.
    2. zu diesem Zeitpunkt "rasen" wir dann durch alle aneinanderstehenden offenen Türen - wie als würde Petra sprinten, immerhin will sie zum Grabmal! Dies tun wir wie folgt:
        1. solange die Tür an unserer Position zu dieser Zeit offen ist, erhöhe die Position um eins.
    3. wir wiederholen diese Prozedur, bis wir beim Grabmal sind.

**Uns ist die Limitation bewusst**, dass Petra in einigen Szenarien von einem Abschnitt förmlich "zerquetscht" werden könnte, während sie darauf wartet, dass der Abschnitt vor ihr endlich aufgeht. Das ist... ungünstig. Wir sind jedoch zeitlich nicht mehr in der Lage gewesen, dieses Problem zu beheben. Die derzeitige Lösung ist zwar schnell und für einige Eingaben anwendbar, aber trägt nun mal diesen Fehler.

## Wichtigste Teile des Quelltextes

Dieser Teil lässt Petra durch die Abschnitte sausen und das Grabmal finden:

```python
def solve(intervals: "list[int]") -> "tuple[list[tuple[int, int]], int]":
    """
    Ermittelt die Dauern, die man warten muss.
    """

    intervals = [-1] + intervals  # wir stehen zu beginn bei keinem Block.

    res: "list[tuple[int, int, int]]" = []
    time = 0
    pos = 0

    while pos < len(intervals) - 1:
        waitFor = timeTillOpenOrClose(intervals[pos + 1], time)
        time += waitFor

        if waitFor > timeTillOpenOrClose(intervals[pos], time - waitFor):
            # ... Erklärungen und fortführende Gedanken
            # => siehe Quelltext-Datei
            pass

        # Der Gang vor uns muss jetzt offen sein. Gut! Eins weiter könnten wir schon.
        # Aber können wir noch weiter? Mal testen:
        while pos < len(intervals) - 1 and isBlockOpen(intervals[pos + 1], time):
            pos += 1

        res.append((waitFor, pos, time))

    return ([(el[0], el[1]) for el in res], time)
```

## Ausgaben des Programms

Folgend die Ausgaben des Programms bei allen Beispielen:

```
user@testpc:~/bwinf$ python3 grabmal.py grabmal0.txt
Schritte: Warte 5 Minuten und gehe dann zum Abschnitt 1 weiter. Warte 3 Minuten und gehe dann zum Abschnitt 2 weiter. Warte 4 Minuten und gehe dann zum Abschnitt 3 weiter. Zeit benötigt: 12 Minuten

user@testpc:~/bwinf$ python3 grabmal.py grabmal1.txt
Schritte: Warte 17 Minuten und gehe dann zum Abschnitt 2 weiter. Warte 4 Minuten und gehe dann zum Abschnitt 3 weiter. Warte 6 Minuten und gehe dann zum Abschnitt 4 weiter. Warte 12 Minuten und gehe dann zum Abschnitt 5 weiter. Zeit benötigt: 39 Minuten

user@testpc:~/bwinf$ python3 grabmal.py grabmal2.txt
Schritte: Warte 170000 Minuten und gehe dann zum Abschnitt 2 weiter. Warte 40009 Minuten und gehe dann zum Abschnitt 3 weiter. Warte 59991 Minuten und gehe dann zum Abschnitt 4 weiter. Warte 120003 Minuten und gehe dann zum Abschnitt 5 weiter. Zeit benötigt: 390003 Minuten

user@testpc:~/bwinf$ python3 grabmal.py grabmal3.txt
Schritte: Warte 4 Minuten und gehe dann zum Abschnitt 1 weiter. Warte 18 Minuten und gehe dann zum Abschnitt 6 durch. Warte 1 Minuten und gehe dann zum Abschnitt 9 durch. Warte 3 Minuten und gehe dann zum Abschnitt 10 weiter. Zeit benötigt: 26 Minuten

user@testpc:~/bwinf$ python3 grabmal.py grabmal4.txt
Schritte: Warte 72063 Minuten und gehe dann zum Abschnitt 1 weiter. Warte 312 Minuten und gehe dann zum Abschnitt 2 weiter. Warte 15330 Minuten und gehe dann zum Abschnitt 3 weiter. Warte 43365 Minuten und gehe dann zum Abschnitt 5 durch. Warte 51180 Minuten und gehe dann zum Abschnitt 6 weiter. Warte 5617 Minuten und gehe dann zum Abschnitt 7 weiter. Warte 72785 Minuten und gehe dann zum Abschnitt 8 weiter. Warte 22939 Minuten und gehe dann zum Abschnitt 10 durch. Zeit benötigt: 283591 Minuten

user@testpc:~/bwinf$ python3 grabmal.py grabmal5.txt
Schritte: Warte 5988 Minuten und gehe dann zum Abschnitt 1 weiter. Warte 403 Minuten und gehe dann zum Abschnitt 3 durch. Warte 1778 Minuten und gehe dann zum Abschnitt 4 weiter. Warte 1228 Minuten und gehe dann zum Abschnitt 9 durch. Warte 2759 Minuten und gehe dann zum Abschnitt 15 durch. Warte 1549 Minuten und gehe dann zum Abschnitt 18 durch. Warte 5951 Minuten und gehe dann zum Abschnitt 19 weiter. Warte 1904 Minuten und gehe dann zum Abschnitt 20 weiter. Warte 955 Minuten und gehe dann zum Abschnitt 21 weiter. Warte 957 Minuten und gehe dann zum Abschnitt 26 durch. Warte 1548 Minuten und gehe dann zum Abschnitt 27 weiter. Warte 3800 Minuten und gehe dann zum Abschnitt 28 weiter. Warte 469 Minuten und gehe dann zum Abschnitt 29 weiter. Warte 141 Minuten und gehe dann zum Abschnitt 33 durch. Warte 186 Minuten und gehe dann zum Abschnitt 34 weiter. Warte 3179 Minuten und gehe dann zum Abschnitt 35 weiter. Warte 2597 Minuten und gehe dann zum Abschnitt 37 durch. Warte 5448 Minuten und gehe dann zum Abschnitt 39 durch. Warte 232 Minuten und gehe dann zum Abschnitt 40 weiter. Warte 340 Minuten und gehe dann zum Abschnitt 42 durch. Warte 1050 Minuten und gehe dann zum Abschnitt 43 weiter. Warte 1846 Minuten und gehe dann zum Abschnitt 44 weiter. Warte 2347 Minuten und gehe dann zum Abschnitt 46 durch. Warte 3835 Minuten und gehe dann zum Abschnitt 50 durch. Warte 915 Minuten und gehe dann zum Abschnitt 57 durch. Warte 4816 Minuten und gehe dann zum Abschnitt 58 weiter. Warte 3386 Minuten und gehe dann zum Abschnitt 59 weiter. Warte 1415 Minuten und gehe dann zum Abschnitt 61 durch. Warte 348 Minuten und gehe dann zum Abschnitt 62 weiter. Warte 4787 Minuten und gehe dann zum Abschnitt 66 durch. Warte 1396 Minuten und gehe dann zum Abschnitt 67 weiter. Warte 3637 Minuten und gehe dann zum Abschnitt 69 durch. Warte 2568 Minuten und gehe dann zum Abschnitt 71 durch. Warte 3065 Minuten und gehe dann zum Abschnitt 72 weiter. Warte 583 Minuten und gehe dann zum Abschnitt 73 weiter. Warte 2667 Minuten und gehe dann zum Abschnitt 77 durch. Warte 150 Minuten und gehe dann zum Abschnitt 79 durch. Warte 297 Minuten und gehe dann zum Abschnitt 80 weiter. Warte 743 Minuten und gehe dann zum Abschnitt 81 weiter. Warte 6110 Minuten und gehe dann zum Abschnitt 83 durch. Warte 1394 Minuten und gehe dann zum Abschnitt 84 weiter. Warte 5118 Minuten und gehe dann zum Abschnitt 85 weiter. Zeit benötigt: 93885 Minuten
```

_93885 Minuten?! Da muss Petra aber lange warten. Hoffentlich hat sie Proviant dabei._
