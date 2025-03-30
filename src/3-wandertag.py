#!/usr/bin/python3

"""
Lösungen für die Aufgabe 3 ("Wandertag") des 43. Bundeswettbewerbs Informatik.
"""

from copy import deepcopy
import sys
import os


NUM_OF_TRACKS_WANTED = (
    3  # Anzahl der zu berechnenden sowie auszugebenden Strecken
)


def read_file(filename: str = "wandern.txt") -> "list[tuple[int, int]]":
    """
    Liest eine Eingabedatei ein und gibt einen geparsten Wert (Liste mit Tupeln der Minimal-, Maximalwerte und Indizes) zurück.
    Referenz: https://bwinf.de/bundeswettbewerb/43/ (Unterpunkt "Wandertag")
    """

    res = []

    if not os.path.isfile(filename):
        # Anscheinend gibt es die gewollte Eingabedatei auf dem Dateisystem nicht.
        print("Fehler: Die angegebene Datei existiert nicht.")

    with open(filename, "r") as f:
        for index, line in enumerate(f.readlines()):
            if index == 0 or not line:
                # Erste oder leere Zeile(n) überspringen (wir brauchen die Anzahl an Teilnehmer*innenwünschen hier nicht)
                continue

            try:
                line_nums: "list[str]" = line.split()
                to_add: "tuple[int, int, int]" = tuple(
                    (*(int(i) for i in line_nums), index)
                )
                res.append(to_add)

                assert len(to_add) == 3

            except ValueError:
                # Da hat etwas nicht funktioniert!
                print(f"Fehler: fehlgeformte Werte in Zeile {index+1}.")
                sys.exit(3)
            except AssertionError:
                # Oh - in dieser Zeile sind wohl entweder zu viele oder zu wenige Werte vorhanden gewesen.
                print(f"Fehler: Falsche Anzahl an Werten in Zeile {index+1}")
                sys.exit(3)

    return res


def find_people_matching(
    list_: "list[tuple[int, int, int]]", track_length: int
) -> "tuple[list[int], list[int]]":
    """
    Findet alle passenden Teilnehmer*innen, gibt einen Tupel aus einer Liste mit den matchenden Indizes der lokalen Liste
    und den matchenden Indizes der absoluten Liste (aus Eingabedatei) zurück.
    """
    matching_local = []
    matching_global = []

    for index, element in enumerate(list_):
        if element[0] <= track_length <= element[1]:
            matching_global.append(element[2])
            matching_local.append(index)

    return (matching_global, matching_local)


def main() -> None:
    """
    Die Hauptmethode - hier geschiet die grundlegende Ablauflogik des Programms.
    """

    if len(sys.argv) != 2:
        print("Nutzung: python3 wandertag.py NAME_DER_EINGABEDATEI.txt")
        sys.exit(1)

    values: "list[tuple[int, int, int]]" = read_file(sys.argv[1])
    values_copy: "list[tuple[int, int, int]]" = deepcopy(values)
    total_num_entries: int = len(values)

    results: "dict[int, tuple[int, list[int]]]" = {}
    # Ergebnis-Dictionary; enthält die bestmöglich Streckenlänge als Key und als Value einen Tupel aus Teilnehmer*innenanzahl und den Indizes derer.

    for j in range(NUM_OF_TRACKS_WANTED):
        max_num_matches: int = -1
        best_length_found: int = -1
        participants: "list[int]" = []
        participant_local_indices: "list[int]" = []

        min_dist: int = min(values, key=lambda x: x[0])[0]
        max_dist: int = max(values, key=lambda x: x[1])[1]

        for index in range(min_dist, max_dist):
            potential_participants, matching_local_indices = (
                find_people_matching(values, index)
            )
            num_participants = len(potential_participants)

            if num_participants > max_num_matches:
                max_num_matches = num_participants
                participants = potential_participants
                participant_local_indices = matching_local_indices
                best_length_found = index

        results[best_length_found] = (len(participants), participants)

        if j == NUM_OF_TRACKS_WANTED - 1:
            # wir müssen nicht wieder die gematchten Personen aus der Liste entfernen, da wir fertig sind
            # und jetzt lieber das Ergebnis direkt ausgeben sollten, anstatt noch mehr kostbare Zeit
            # zu verschwenden.
            break

        for index in sorted(participant_local_indices, reverse=True):
            # Für all diese Leute wissen wir nun: Auf geht's! Sehen wir uns also im nächsten Durchlauf
            # nur die restlichen an.
            del values[index]

    # Nachbearbeitung: Noch die Personen eintragen, die bei unseren Top 3 auch mitkommen würden (sie können zeitgleich laufen)
    for key, value in results.items():
        all_people_attending: "tuple[list[int], list[int]]" = (
            find_people_matching(values_copy, key)[0]
        )
        results[key] = (len(all_people_attending), all_people_attending)

    total_participants: "set[int]" = set()

    print("\nBeste gefundene Streckenlängen:")
    for idx, (key, value) in enumerate(results.items()):
        print(
            f"\t{idx + 1}.)\n\t - Streckenlänge: {key} m"
            f"\n\t - Anzahl der Teilnehmer*innen: {value[0]}"
            f"\n\t - konkrete Indizes der Teilnehmer*innen: {', '.join([str(k) for k in value[1]])}"
        )
        total_participants.update(value[1])

    print(
        f"\nWir konnten {len(total_participants)} von {total_num_entries} Teilnehmer*innen "
        f"({len(total_participants)/total_num_entries*100:.2f}%) mitnehmen!\n"
    )  # weitere "\n"s nur für visuelles extra-Padding eingebaut

    sys.exit(0)


if __name__ == "__main__":
    main()
