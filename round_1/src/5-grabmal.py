#!/usr/bin/python3

"""
Lösungen für die Aufgabe 5 ("Ägyptisches Grabmal") des 43. Bundeswettbewerbs Informatik.
"""

import os
import sys


def main():
    """
    Hauptfunktion des Programms.
    """

    if len(sys.argv) != 2:
        print(
            "Fehler: ungültige Anzahl an Argumenten. Bitte übergebe den Dateinamen der Eingabedatei als Argument."
        )
        sys.exit(3)

    intervals = readFile(sys.argv[1])
    res, time = solve(intervals)
    explanation = generateExplanationFromResult(res)

    print("Schritte:", explanation, "Zeit benötigt:", time, "Minuten")


def generateExplanationFromResult(res: "list[tuple[int, int]]") -> str:
    """
    Generiert eine textliche Erklärung der Schritte, um diese dann auszugeben.
    """

    explanation = ""
    last = 1

    for el in res:
        explanation += f"Warte {el[0]} Minuten und gehe dann zum Abschnitt {el[1]} \
{'durch' if (el[1] - last > 1) else 'weiter'}. "
        last = el[1]

    return explanation.strip()


def isBlockOpen(blockInterval: int, time: int) -> bool:
    return (time // blockInterval) % 2 == 1


def timeTillOpenOrClose(blockInterval: int, time: int) -> int:
    if blockInterval == -1:
        return sys.maxsize  # der erste Block schließt oder öffnet sich nie

    return blockInterval - (time % blockInterval)


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
            # wir schaffen es nicht, in der Zeit, die das nächste Tor zu öffnen braucht,
            # in diesem Abschnitt stehen zu bleiben - also gehen wir um eins zurück

            # nur was dann?
            # das haben wir nicht lösen können...

            # Unser Lösungsansatz war, zurück zur letzten Stell zu gehen, bei der wir
            # sicher wissen, dass sie noch offen ist. Dann warten wir dort, bis wir
            # wieder weitergehen können und versuchen es dann erneut. Praktisch wird
            # iterativ die Menge an Möglichkeiten durchsucht.
            #
            # Leider hat diese Idee keine Früchte getragen. Aufgrund der Klausurenphase
            # sehen wir uns einfach nicht in der Lage, das noch auf den letzten
            # Drücker hinzubekommen. Dieser Lösungsansatz hier funktioniert dennoch
            # für jedes Szenario, in dem das oben genannte Problem nicht auftritt.

            pass  # nichts tun... :(

        # Der Gang vor uns muss jetzt offen sein. Gut! Eins weiter könnten wir schon.
        # Aber können wir noch weiter? Mal testen:
        while pos < len(intervals) - 1 and isBlockOpen(
            intervals[pos + 1], time
        ):
            pos += 1

        res.append((waitFor, pos, time))

    return ([(el[0], el[1]) for el in res], time)


def readFile(filename: str) -> "list[int]":
    """
    Liest die Datei ein und parst diese.
    """

    if not os.path.isfile(filename):
        print("Fehler: Die Datei existiert nicht.")
        sys.exit(1)

    res = []

    with open(filename, "r") as f:
        for index, line in enumerate(f.read().splitlines()):
            if not line:
                continue

            if index == 0:
                continue  # wir brauchen die erste Zeile nicht

            try:
                res.append(int(line))
            except ValueError:
                print(f"Ungültiger Wert auf Zeile {index + 1}")
                sys.exit(2)

    return res


if __name__ == "__main__":
    main()
