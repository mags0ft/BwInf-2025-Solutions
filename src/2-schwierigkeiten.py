#!/usr/bin/python3

"""
Lösungen für die Aufgabe 2 ("Schwierigkeiten") des 43. Bundeswettbewerbs Informatik.
"""

from collections import OrderedDict
import sys


def main() -> None:
    """
    Hauptfunktion des Programms
    """

    filename = sys.argv[1]  # Dateiname aus Argumenten lesen
    __num_exams, __num_tasks, __num_to_sort, lines, to_sort, all_tasks = (
        read_file(filename)
    )  # Datei einlesen

    scores: "dict[str, int]" = {
        i: 100 for i in all_tasks
    }  # Scores initialisieren

    determine_easiest(lines, scores)

    res: "list[str]" = []

    for k, v in insertion_sort_dict(scores).items():
        if k not in to_sort:
            continue  # wir wollen nur die, die sortiert werden sollen

        print(f"{k}: {v}")
        res.append(k)  # Ergebnis speichern

    print(" < ".join(res))


def determine_easiest(
    lines: "list[list[str]]", scores: "dict[str, int]"
) -> None:
    """
    Ermittelt die einfachsten Aufgaben durch ein Scoring-System.
    Aufgaben, die schwerer sind als andere, haben einen höheren Score.
    """

    for line in lines:
        # wir gehen jede Zeile durch
        line_len: int = len(line)
        for idx in range(line_len):
            if idx >= line_len - 1:
                # wenn wir am Ende der Zeile sind, können wir abbrechen
                break

            # wir holen uns die aktuelle und die nächste Aufgabe:
            cur_task: str = line[idx]
            next_task: str = line[idx + 1]
            # wenn die nächste Aufgabe in der Zeile schwerer ist, als die aktuelle,
            # dann erhöhen wir den Score von der schwereren Aufgabe
            scores[next_task] = scores[cur_task] + 1


def read_file(
    filename: str,
) -> "tuple[int, int, int, list[list[str]], list[str], set[str]]":
    """
    Parst die Datei und gibt die Werte zurück.
    Zurückgegeben wird ein Tuple mit folgenden Werten:
    - Anzahl der Prüfungen
    - Anzahl der Aufgaben
    - Anzahl der zu sortierenden Aufgaben
    - Liste der Zeilen
    - Liste der zu sortierenden Aufgaben
    """
    lines: "list[list[str]]" = []
    to_sort: "list[str]" = []
    all_tasks: "set[str]" = set()

    num_exams: int = 0
    num_tasks: int = 0
    num_to_sort: int = 0

    with open(filename, "r") as f:
        for idx, el in enumerate(f.read().splitlines()):
            # wir gehen wieder jede Zeile durch
            if idx == 0:
                # die erste Zeile enthält die Anzahl der Prüfungen,
                # Aufgaben und zu sortierenden Aufgaben
                temp = el.split()
                num_exams = int(temp[0])
                num_tasks = int(temp[1])
                num_to_sort = int(temp[2])
                continue

            if "<" not in el:
                # wir sind in der letzten Zeile!
                to_sort = el.split()
                break

            all_els = el.replace(" ", "").split("<")
            lines.append(all_els)

            for el_ in all_els:
                # wir fügen alle Aufgaben zu einer Menge hinzu
                all_tasks.add(el_)

    return (num_exams, num_tasks, num_to_sort, lines, to_sort, all_tasks)


def insertion_sort_dict(to_sort: "dict[str, int]") -> OrderedDict:
    """
    Sortiert das Ergebnis-Dictionary mithilfe von Insertion Sort.
    Wir haben diese Methode neu implementiert, anstatt Python's built-in
    sorted() zu nutzen, obwohl dieses vermutlich schneller wäre.
    """

    def __swap(list_: "list[str]", pos1: int, pos2: int):
        """
        Private swap-Methode für die Liste `cur_order`.
        """
        temp: str = list_[
            pos1
        ]  # zum Swappen brauchen wir eine temporäre Variable
        list_[pos1] = list_[pos2]
        list_[pos2] = temp

    cur_order: "list[str]" = list(
        to_sort.keys()
    )  # wir erstellen uns eine Liste der Keys, die wir sortieren.

    for idx in range(1, len(cur_order)):
        # nun folgt ein klassisches Insertion Sort:
        j = idx
        while (j > 0) and (to_sort[cur_order[j]] < to_sort[cur_order[j - 1]]):
            __swap(cur_order, j, j - 1)
            j -= 1

    # zu guter Letzt geben wir das ganze als ein Ordered Dict zurück, damit wir unsere harte Arbeit
    # nicht umsonst gemacht haben (okay, streng genommen würde es auch ohne gehen, so ist es aber
    # sauberer und sicherer.)
    return OrderedDict(**{k: to_sort[k] for k in cur_order})


if __name__ == "__main__":
    # wir rufen die Hauptfunktion auf!
    main()
